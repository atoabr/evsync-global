import plotly.express as px
import streamlit as st
from core.calc import hhi
from core.data import minerals

st.set_page_config(page_title="Supply Chain", page_icon="⛏️", layout="wide")
st.title("⛏️ Battery supply chain concentration")
st.caption("Approximate ~2023 shares (seed data). Verify with USGS Mineral Commodity Summaries and IEA. "
           "Roadmap: real trade flows from UN Comtrade (HS 2836, 2605, 7502, 8507).")
m = minerals()
mineral = st.selectbox("Material", list(dict.fromkeys(m.mineral)))
sub = m[m.mineral == mineral]
st.plotly_chart(px.bar(sub, x="stage", y="share_pct", color="country", title=f"{mineral}: share by stage (%)"),
                use_container_width=True)
cols = st.columns(sub.stage.nunique())
for col, (stage, g) in zip(cols, sub.groupby("stage", sort=False)):
    idx = hhi(g[g.country != "Other"].share_pct)
    col.metric(f"{stage} HHI", f"{idx:,.0f}", "highly concentrated" if idx > 2500 else "moderate",
               delta_color="inverse")
first = sub.stage.iloc[0]
geo = sub[(sub.stage == first) & (sub.iso3 != "OTH")]
st.plotly_chart(px.choropleth(geo, locations="iso3", color="share_pct", hover_name="country",
                              color_continuous_scale="Oranges", title=f"{mineral} {first.lower()} share (%)"),
                use_container_width=True)
