"""Refresh data/processed from real sources.
1) IEA Global EV Data Explorer: download CSV to data/raw/iea_ev.csv
   (columns: region, category, parameter, mode, powertrain, year, unit, value).
2) World Bank API: net energy imports (EG.IMP.CONS.ZS) added as wb_energy_import_pct.
Run:  python scripts/build_data.py"""
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
PROC, RAW = ROOT / "data" / "processed", ROOT / "data" / "raw"


def refresh_ev_share():
    f = RAW / "iea_ev.csv"
    if not f.exists():
        print("No data/raw/iea_ev.csv found; skipping EV share refresh.")
        return
    d = pd.read_csv(f)
    d = d[(d.parameter == "EV sales share") & (d["mode"] == "Cars") & (d.category == "Historical")]
    d = d.groupby(["region", "year"], as_index=False).value.sum().rename(columns={"region": "country", "value": "ev_share"})
    c = pd.read_csv(PROC / "countries.csv")[["country", "iso3"]]
    out = d.merge(c, on="country")[["country", "iso3", "year", "ev_share"]]
    out.to_csv(PROC / "ev_share_history.csv", index=False)
    print(f"EV share history refreshed for {out.country.nunique()} countries")


def refresh_worldbank():
    c = pd.read_csv(PROC / "countries.csv")
    vals = {}
    for iso in c.iso3:
        try:
            r = requests.get(f"https://api.worldbank.org/v2/country/{iso}/indicator/EG.IMP.CONS.ZS",
                             params={"format": "json", "mrv": 1}, timeout=20).json()
            vals[iso] = r[1][0]["value"] if r[1] else None
        except Exception as e:
            print("WB failed for", iso, e)
    c["wb_energy_import_pct"] = c.iso3.map(vals)
    c.to_csv(PROC / "countries.csv", index=False)
    print("World Bank indicator added")


OWID_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"


def refresh_owid_grid():
    """Latest grid carbon intensity (gCO2/kWh) and renewables share of electricity from OWID (Ember data)."""
    d = pd.read_csv(OWID_URL, usecols=["iso_code", "year", "carbon_intensity_elec", "renewables_share_elec"])
    d = d.dropna(subset=["carbon_intensity_elec"]).sort_values("year").groupby("iso_code").tail(1)
    c = pd.read_csv(PROC / "countries.csv")
    m = c.merge(d, left_on="iso3", right_on="iso_code", how="left")
    c["grid_gco2_kwh"] = m.carbon_intensity_elec.fillna(c.grid_gco2_kwh).round(0).values
    c["renewables_share_elec"] = m.renewables_share_elec.round(1).values
    c["grid_year"] = m.year.values
    c.to_csv(PROC / "countries.csv", index=False)
    print("OWID grid intensity refreshed")


if __name__ == "__main__":
    refresh_ev_share()
    refresh_worldbank()
    refresh_owid_grid()
