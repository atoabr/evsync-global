"""CrewAI tools. Numbers come from deterministic functions in core/, never from the LLM."""
import json
import requests
from crewai.tools import tool
from core import calc
from core.data import country_row, country_history, minerals


@tool("country_snapshot")
def country_snapshot(iso3: str) -> str:
    """Seed facts for a country by ISO3 code: fuel/electricity prices, grid carbon intensity,
    oil import share, fleet size, segment focus, and stored policy target (verify with web search)."""
    return json.dumps(country_row(iso3), default=str)


@tool("worldbank_indicator")
def worldbank_indicator(iso3: str, indicator: str) -> str:
    """Latest values of a World Bank indicator for a country. Example indicators:
    NY.GDP.PCAP.CD (GDP per capita), EG.IMP.CONS.ZS (net energy imports % of use),
    EG.ELC.RNEW.ZS (renewable electricity %), SP.POP.TOTL (population)."""
    url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator}"
    try:
        r = requests.get(url, params={"format": "json", "per_page": 8, "mrv": 5}, timeout=20)
        r.raise_for_status()
        data = r.json()[1] or []
        rows = [{"year": d["date"], "value": d["value"]} for d in data if d["value"] is not None]
        # cite the human-readable World Bank data page, not the raw API (which opens as XML)
        iso2 = (data[0].get("country", {}).get("id") if data else None) or iso3[:2]
        page = f"https://data.worldbank.org/indicator/{indicator}?locations={iso2}"
        return json.dumps({"source": page, "series": rows,
                           "note": "Cite the source URL as given. Empty recent years mean the latest data is older."})
    except Exception as e:  # network/API failure must not crash the crew
        return json.dumps({"error": str(e), "source": url})


@tool("tco_calculator")
def tco_calculator(price_ev: float, price_ice: float, km_year: float, elec_usd_kwh: float,
                   fuel_usd_l: float, kwh_100km: float = 16, l_100km: float = 8,
                   years: int = 8, subsidy_usd: float = 0) -> str:
    """Total cost of ownership of an EV vs a petrol vehicle in USD. Use country prices from
    country_snapshot. Typical vehicle defaults: car 35000/28000, 2-wheeler 1500/1200."""
    out = calc.tco(price_ev, price_ice, km_year, elec_usd_kwh, fuel_usd_l,
                   kwh_100km, l_100km, years, subsidy=subsidy_usd)
    out["assumptions"] = (f"EV ${price_ev:,.0f} vs petrol ${price_ice:,.0f}, {km_year:,.0f} km/year, "
                          f"electricity ${elec_usd_kwh}/kWh, fuel ${fuel_usd_l}/L, {years} years, "
                          f"subsidy ${subsidy_usd:,.0f}")
    return json.dumps(out)


@tool("ev_share_forecast")
def ev_share_forecast(iso3: str, target_share: float = 0) -> str:
    """S-curve forecast of EV new-sales share for a country using stored history.
    Returns 2030/2035 share, 50% year and the year a target_share (%) is reached (0 = skip)."""
    h = country_history(iso3)
    try:
        out = calc.forecast_s_curve(h.year, h.ev_share, target_share=target_share or None)
    except Exception as e:
        return json.dumps({"error": str(e)})
    keep = {k: out[k] for k in ("share_2030", "share_2035", "year_50pct", "k")}
    keep["year_reaching_target"] = out.get("year_reaching_target")
    i35 = out["years"].index(2035)
    keep["range_2035_p10_p90"] = [round(out["lo"][i35], 1), round(out["hi"][i35], 1)]
    return json.dumps(keep)


OIL_USD_BBL = 80.0  # one global assumption so every country's briefing is comparable


@tool("oil_displacement")
def oil_displacement(iso3: str, fleet_ev_share_pct: float, vehicle_type: str = "Car") -> str:
    """Barrels/day of petrol displaced, import bill avoided and net CO2 avoided if
    fleet_ev_share_pct % of a country's vehicles were electric. vehicle_type: 2-wheeler, 3-wheeler, Car, Bus.
    Uses a fixed oil price of $80/bbl for all countries (do not change it)."""
    r, v = country_row(iso3), calc.VEHICLES[vehicle_type]
    evs = r["vehicles_millions"] * 1e6 * fleet_ev_share_pct / 100
    out = calc.oil_displacement(evs, v["km_year"], v["l_100"], OIL_USD_BBL,
                                r["oil_import_pct"], v["kwh_100"], r["grid_gco2_kwh"])
    out["assumptions"] = (f"{fleet_ev_share_pct}% of {vehicle_type} fleet ({evs:,.0f} vehicles), "
                          f"{v['km_year']:,} km/year, {v['l_100']} L/100km, {v['kwh_100']} kWh/100km, "
                          f"oil ${OIL_USD_BBL:.0f}/bbl, oil import share {r['oil_import_pct']}%, "
                          f"grid {r['grid_gco2_kwh']} gCO2/kWh")
    return json.dumps(out)


@tool("mineral_concentration")
def mineral_concentration(mineral: str) -> str:
    """Supply-chain concentration (shares by country and HHI per stage) for Lithium, Cobalt,
    Nickel, Graphite or 'Battery cells'. Approximate ~2023 seed data; cite USGS/IEA for updates."""
    m = minerals()
    m = m[m.mineral.str.lower() == mineral.lower()]
    out = {}
    for stage, g in m.groupby("stage"):
        named = g[g.country != "Other"]
        out[stage] = {"shares_pct": dict(zip(g.country, g.share_pct)),
                      "hhi_named_countries": round(calc.hhi(named.share_pct), 0)}
    return json.dumps(out)
