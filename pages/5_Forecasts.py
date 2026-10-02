import plotly.graph_objects as go
import streamlit as st
from core import calc
from core.data import countries, history

st.set_page_config(page_title="Forecasts", page_icon="📈", layout="wide")
st.title("📈 Adoption forecast (S-curve)")
c, h = countries(), history()
country = st.selectbox("Country", c.country.tolist(), index=c.country.tolist().index("Canada"))
row = c[c.country == country].iloc[0]
default = float(row.target_share) if row.target_share == row.target_share else 50.0
target = st.slider("Target share of new sales (%)", 5, 100, int(default))
hh = h[h.country == country]
try:
    f = calc.forecast_s_curve(hh.year, hh.ev_share, target_share=target)
except Exception as e:
    st.error(f"Could not fit: {e}")
    st.stop()
fig = go.Figure()
fig.add_scatter(x=f["years"], y=f["hi"], line=dict(width=0), showlegend=False)
fig.add_scatter(x=f["years"], y=f["lo"], fill="tonexty", line=dict(width=0), name="10-90% range")
fig.add_scatter(x=f["years"], y=f["median"], name="Forecast", line=dict(width=3))
fig.add_scatter(x=hh.year, y=hh.ev_share, mode="markers", name="History")
fig.add_hline(y=target, line_dash="dash")
fig.update_layout(yaxis_title="EV share of new sales (%)", xaxis_range=[hh.year.min(), 2045])
st.plotly_chart(fig, use_container_width=True)
a, b, d = st.columns(3)
a.metric("2030", f"{f['share_2030']:.0f}%")
b.metric("2035", f"{f['share_2035']:.0f}%")
d.metric(f"Reaches {target}%", f["year_reaching_target"] or "after 2050")
st.caption("Fitted on only 6 seed points with ceiling 100%; low-share countries carry wide uncertainty. "
           "Improve by fitting on analog countries and longer IEA history.")
