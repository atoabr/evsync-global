import plotly.express as px
import streamlit as st
from core import calc
from core.data import countries, history

st.set_page_config(page_title="EVSync Global", page_icon="⚡", layout="wide")
st.title("⚡ EVSync Global: Global Dashboard")
st.caption("Multi-agent EV transition intelligence: policy, supply chain, cost, oil displacement, forecasts.")
st.warning("Seed data is illustrative. Use the AI Analyst page for live, sourced research and verify before decisions.")

c, h = countries(), history()
latest = h[h.year == h.year.max()]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Countries covered", len(c))
k2.metric(f"Median EV share {h.year.max()}", f"{latest.ev_share.median():.1f}%")
k3.metric("Highest share", f"{latest.loc[latest.ev_share.idxmax(), 'country']} ({latest.ev_share.max():.0f}%)")
tot = 0
for _, r in c.iterrows():  # illustrative: 10% of every fleet electrified
    tot += calc.oil_displacement(r.vehicles_millions * 1e6 * 0.10, 12000, 6, 80, r.oil_import_pct, 16,
                                 r.grid_gco2_kwh)["barrels_per_day"]
k4.metric("Oil saved at 10% fleet EV", f"{tot/1e6:.2f} M bbl/day")

fig = px.choropleth(latest, locations="iso3", color="ev_share", hover_name="country",
                    color_continuous_scale="Viridis", title=f"EV share of new sales, {h.year.max()} (%)")
st.plotly_chart(fig, use_container_width=True)
fig2 = px.line(h, x="year", y="ev_share", color="country", markers=True, title="Adoption trajectories")
st.plotly_chart(fig2, use_container_width=True)
st.caption("Use the sidebar to open the other pages.")
