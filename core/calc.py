"""Deterministic maths used by BOTH the Streamlit pages and the CrewAI tools.
Agents call these functions instead of guessing numbers."""
import numpy as np
from scipy.optimize import curve_fit

# Defaults per vehicle type: price EV, price ICE (USD), kWh/100km, L/100km, km/year
VEHICLES = {
    "2-wheeler": dict(price_ev=1500, price_ice=1200, kwh_100=3, l_100=2.2, km_year=8000),
    "3-wheeler": dict(price_ev=3500, price_ice=3000, kwh_100=8, l_100=4.0, km_year=20000),
    "Car":       dict(price_ev=35000, price_ice=28000, kwh_100=16, l_100=8.0, km_year=15000),
    "Bus":       dict(price_ev=400000, price_ice=250000, kwh_100=120, l_100=35.0, km_year=60000),
}
LITRES_PER_BARREL = 159.0
CO2_KG_PER_LITRE_PETROL = 2.31


def tco(price_ev, price_ice, km_year, elec_kwh, fuel_l, kwh_100=16, l_100=8,
        years=8, ev_maint=0.02, ice_maint=0.04, subsidy=0.0):
    """Total cost of ownership (undiscounted) for an EV vs an ICE vehicle."""
    ev_energy = km_year / 100 * kwh_100 * elec_kwh
    ice_energy = km_year / 100 * l_100 * fuel_l
    ev_annual = ev_energy + ev_maint * price_ev
    ice_annual = ice_energy + ice_maint * price_ice
    ev_total = price_ev - subsidy + ev_annual * years
    ice_total = price_ice + ice_annual * years
    gap = price_ev - subsidy - price_ice
    if gap <= 0:
        breakeven = 0.0
    elif ice_annual > ev_annual:
        breakeven = gap / (ice_annual - ev_annual)
    else:
        breakeven = None  # EV never pays back on running costs
    return {"ev_total": round(ev_total), "ice_total": round(ice_total),
            "savings": round(ice_total - ev_total),
            "breakeven_years": None if breakeven is None else round(breakeven, 1),
            "ev_annual_energy": round(ev_energy), "ice_annual_energy": round(ice_energy)}


def logistic(t, ceiling, k, t0):
    return ceiling / (1 + np.exp(-k * (t - t0)))


def forecast_s_curve(years, shares, end_year=2050, target_share=None, ceiling=100.0,
                     n_draws=300, seed=0):
    """Fit an S-curve (ceiling fixed) to EV sales share (%) and forecast with a 10-90% band."""
    x = np.asarray(years, dtype=float)
    y = np.asarray(shares, dtype=float)
    if len(x) < 4:
        raise ValueError("Need at least 4 historical points")
    f = lambda t, k, t0: logistic(t, ceiling, k, t0)  # noqa: E731
    popt, pcov = curve_fit(f, x, y, p0=[0.5, x.max() + 3], bounds=([0.02, x.min() - 5], [0.8, 2100]),
                           maxfev=20000)
    grid = np.arange(int(x.min()), end_year + 1)
    median = f(grid, *popt)
    lo, hi = median, median
    if np.all(np.isfinite(pcov)):
        rng = np.random.default_rng(seed)
        draws = rng.multivariate_normal(popt, pcov, size=n_draws)
        draws = draws[(draws[:, 0] > 0.02) & (draws[:, 0] < 0.8)]
        if len(draws):
            curves = np.array([f(grid, *d) for d in draws])
            lo, hi = np.percentile(curves, 10, axis=0), np.percentile(curves, 90, axis=0)
    out = {"years": grid.tolist(), "median": median.tolist(), "lo": np.asarray(lo).tolist(),
           "hi": np.asarray(hi).tolist(), "k": float(popt[0]), "year_50pct": float(popt[1]),
           "share_2030": float(f(2030, *popt)), "share_2035": float(f(2035, *popt))}
    if target_share is not None:
        hit = grid[median >= target_share]
        out["year_reaching_target"] = int(hit[0]) if len(hit) else None
    return out


def oil_displacement(evs, km_year, l_100, oil_usd_bbl, oil_import_pct, kwh_100, grid_gco2):
    """Gasoline displaced by `evs` vehicles and the resulting import bill / CO2 effects."""
    litres = evs * km_year / 100 * l_100
    bpd = litres / LITRES_PER_BARREL / 365
    import_bill = bpd * 365 * oil_usd_bbl * oil_import_pct / 100
    co2_ice_t = litres * CO2_KG_PER_LITRE_PETROL / 1000
    kwh = evs * km_year / 100 * kwh_100
    co2_ev_t = kwh * grid_gco2 / 1e6
    return {"barrels_per_day": round(bpd), "import_bill_avoided_usd_yr": round(import_bill),
            "extra_electricity_gwh_yr": round(kwh / 1e6, 1),
            "co2_avoided_tonnes_yr": round(co2_ice_t - co2_ev_t),
            "gross_petrol_co2_tonnes": round(co2_ice_t), "ev_grid_co2_tonnes": round(co2_ev_t)}


def hhi(shares_pct):
    """Herfindahl-Hirschman index (0-10,000) from percentage shares. >2,500 = highly concentrated.
    'Other' should be excluded or split before calling."""
    return float(sum((s) ** 2 for s in shares_pct))
