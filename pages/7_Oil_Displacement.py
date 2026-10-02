import pandas as pd
import plotly.express as px
import streamlit as st
from core import calc
from core.data import countries

st.set_page_config(page_title="Oil Displacement", page_icon="🛢️", layout="wide")
st.title("🛢️ Oil displacement and energy security")
c = countries().set_index("country")
country = st.selectbox("Country", c.index.tolist(), index=list(c.index).index("Pakistan"))
r = c.loc[country]
vt = st.radio("Electrified vehicle type", list(calc.VEHICLES), horizontal=True, index=2)
d = calc.VEHICLES[vt]
oil = st.number_input("Oil price (USD/barrel)", value=80.0)
share = st.slider("Share of national fleet electrified (%)", 1, 60, 10)

def run(pct):
    return calc.oil_displacement(r.vehicles_millions * 1e6 * pct / 100, d["km_year"], d["l_100"], oil,
                                 r.oil_import_pct, d["kwh_100"], r.grid_gco2_kwh)
res = run(share)
a, b, e, f = st.columns(4)
a.metric("Petrol displaced", f"{res['barrels_per_day']:,} bbl/day")
b.metric("Import bill avoided", f"${res['import_bill_avoided_usd_yr']/1e6:,.0f} M/yr")
e.metric("Net CO2 avoided", f"{res['co2_avoided_tonnes_yr']/1e6:,.2f} Mt/yr")
f.metric("Extra electricity", f"{res['extra_electricity_gwh_yr']:,} GWh/yr")
sweep = pd.DataFrame([{"fleet_share_pct": p, **run(p)} for p in range(1, 61)])
st.plotly_chart(px.line(sweep, x="fleet_share_pct", y="import_bill_avoided_usd_yr",
                        title="Import bill avoided vs electrification level"), use_container_width=True)
st.caption(f"Grid: {r.grid_gco2_kwh} gCO2/kWh, oil import share {r.oil_import_pct}%. A dirty grid lowers CO2 "
           "gains: electric mobility is cleanest when paired with renewables. Seed data is approximate.")
