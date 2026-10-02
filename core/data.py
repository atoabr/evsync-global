from functools import lru_cache
from pathlib import Path
import pandas as pd

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"

@lru_cache(maxsize=None)
def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)

def countries() -> pd.DataFrame:
    return _read("countries.csv").copy()

def history() -> pd.DataFrame:
    return _read("ev_share_history.csv").copy()

def minerals() -> pd.DataFrame:
    return _read("minerals.csv").copy()

def country_row(iso3: str) -> dict:
    df = _read("countries.csv")
    hit = df[df.iso3 == iso3.upper()]
    if hit.empty:
        raise KeyError(f"Unknown country code: {iso3}")
    return hit.iloc[0].to_dict()

def country_history(iso3: str) -> pd.DataFrame:
    h = _read("ev_share_history.csv")
    return h[h.iso3 == iso3.upper()].sort_values("year").copy()
