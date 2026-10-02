"""Run the CrewAI crew for a list of countries and save briefings to data/precached/ (commit them!).
Usage:
  python scripts/precache.py                       # default 8 countries, Policymaker, English
  python scripts/precache.py PAK CAN --audience Investor --language French
Cost: roughly 1 crew run per country/audience/language. Test with ONE country first."""
import argparse
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.data import country_row  # noqa: E402
from core.env import load_env  # noqa: E402

DEFAULT = ["PAK", "CAN", "USA", "GBR", "IND", "DEU", "NOR", "IDN"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3", nargs="*", default=DEFAULT)
    ap.add_argument("--audience", default="Policymaker", choices=["Policymaker", "Investor", "Manufacturer"])
    ap.add_argument("--language", default="English")
    ap.add_argument("--force", action="store_true", help="overwrite existing briefings")
    a = ap.parse_args()
    load_env()
    from agents.crew import EVSyncCrew  # after env is loaded
    out_dir = ROOT / "data" / "precached"
    out_dir.mkdir(exist_ok=True)
    failed = []
    for iso in a.iso3:
        f = out_dir / f"{iso}_{a.audience}_{a.language}.md"
        if f.exists() and not a.force:
            print(f"skip {iso} (exists)")
            continue
        name = country_row(iso)["country"]
        for attempt in (1, 2):
            try:
                print(f"== {name} ({iso}) attempt {attempt}")
                res = EVSyncCrew().crew().kickoff(inputs={"country": name, "iso3": iso,
                                                           "audience": a.audience, "language": a.language,
                                                           "today": date.today().isoformat(), "year": str(date.today().year)})
                f.write_text(res.raw)
                print("saved", f)
                break
            except Exception as e:
                print("failed:", e)
                time.sleep(10)
        else:
            failed.append(iso)
    print("Done. Failed:", failed or "none")


if __name__ == "__main__":
    main()
