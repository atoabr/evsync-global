import pytest
from core import calc
from core.briefing import offline_brief


def test_tco_known_values():
    r = calc.tco(30000, 25000, 10000, 0.10, 1.5, 16, 8, 8)
    # EV: 30000 + 8*(1600*0.10... ) computed by hand
    ev_annual = 10000 / 100 * 16 * 0.10 + 0.02 * 30000  # 160 + 600
    ice_annual = 10000 / 100 * 8 * 1.5 + 0.04 * 25000   # 1200 + 1000
    assert r["ev_total"] == round(30000 + 8 * ev_annual)
    assert r["ice_total"] == round(25000 + 8 * ice_annual)
    assert r["breakeven_years"] == pytest.approx(5000 / (ice_annual - ev_annual), abs=0.1)


def test_tco_never_breaks_even():
    r = calc.tco(50000, 20000, 1000, 0.5, 0.5)
    assert r["breakeven_years"] is None


def test_forecast_monotonic_and_target():
    yrs = [2019, 2020, 2021, 2022, 2023, 2024]
    f = calc.forecast_s_curve(yrs, [3, 4, 5, 7, 9, 12], target_share=50)
    assert f["median"] == sorted(f["median"])
    assert 2025 < f["year_reaching_target"] < 2050
    assert all(lo <= hi for lo, hi in zip(f["lo"], f["hi"]))


def test_forecast_needs_data():
    with pytest.raises(ValueError):
        calc.forecast_s_curve([2023, 2024], [1, 2])


def test_oil_displacement_math():
    r = calc.oil_displacement(1_000_000, 12000, 8, 80, 100, 16, 0)
    litres = 1_000_000 * 12000 / 100 * 8
    assert r["barrels_per_day"] == round(litres / 159 / 365)
    assert r["co2_avoided_tonnes_yr"] == round(litres * 2.31 / 1000)


def test_hhi():
    assert calc.hhi([50, 50]) == 5000


@pytest.mark.parametrize("iso", ["CAN", "PAK", "NOR", "ETH"])
def test_offline_brief_runs(iso):
    assert "EV transition snapshot" in offline_brief(iso)
