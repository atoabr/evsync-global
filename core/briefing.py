"""Deterministic, no-API-key briefing. Used as offline demo fallback."""
from datetime import date
from core import calc
from core.data import country_row, country_history


def offline_brief(iso3: str, audience: str = "Policymaker") -> str:
    r = country_row(iso3)
    h = country_history(iso3)
    car, tw = calc.VEHICLES["Car"], calc.VEHICLES["2-wheeler"]
    t_car = calc.tco(car["price_ev"], car["price_ice"], car["km_year"], r["elec_usd_kwh"],
                     r["petrol_usd_l"], car["kwh_100"], car["l_100"])
    t_2w = calc.tco(tw["price_ev"], tw["price_ice"], tw["km_year"], r["elec_usd_kwh"],
                    r["petrol_usd_l"], tw["kwh_100"], tw["l_100"])
    tgt = r["target_share"] if r["target_share"] == r["target_share"] else None
    fc = calc.forecast_s_curve(h.year, h.ev_share, target_share=tgt)
    fleet = r["vehicles_millions"] * 1e6 * 0.10
    oil = calc.oil_displacement(fleet, 12000, 6.0, 80, r["oil_import_pct"], 16, r["grid_gco2_kwh"])
    return f"""# EV transition snapshot: {r['country']} ({audience} view)
*Offline deterministic briefing, {date.today()}. Seed data is illustrative; run the AI Analyst with API keys for live, sourced research.*

**Archetype:** {r['archetype']}  |  **Primary segment:** {r['primary_segment']}

## Policy
{r['target_note']} (seed data; verify current status)

## Cost of ownership (8 years, local prices)
- Car: EV ${t_car['ev_total']:,} vs petrol ${t_car['ice_total']:,} -> savings **${t_car['savings']:,}**, breakeven {t_car['breakeven_years']} yrs
- 2-wheeler: EV ${t_2w['ev_total']:,} vs petrol ${t_2w['ice_total']:,} -> savings **${t_2w['savings']:,}**, breakeven {t_2w['breakeven_years']} yrs

## Forecast (S-curve fit)
Projected EV sales share: **{fc['share_2030']:.0f}% by 2030**, **{fc['share_2035']:.0f}% by 2035**; 50% point around {fc['year_50pct']:.0f}.
{'Target year reaching ' + str(tgt) + '%: ' + str(fc.get('year_reaching_target')) if tgt else 'No numeric national target in seed data.'}

## Oil displacement if 10% of the fleet electrified
~**{oil['barrels_per_day']:,} barrels/day** of petrol displaced, import bill avoided ~**${oil['import_bill_avoided_usd_yr']:,}/yr**,
net CO2 avoided ~**{oil['co2_avoided_tonnes_yr']:,} t/yr** at a grid intensity of {r['grid_gco2_kwh']} gCO2/kWh.
"""
