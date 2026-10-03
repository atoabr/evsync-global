import plotly.express as px
import streamlit as st
from core.data import countries, history

st.set_page_config(page_title="Compare", page_icon="🌍", layout="wide")
st.title("🌍 Country comparison")
c, h = countries(), history()
sel = st.multiselect("Choose 2-4 countries", c.country.tolist(), default=["Canada", "Pakistan"], max_selections=4)
if sel:
    st.plotly_chart(px.line(h[h.country.isin(sel)], x="year", y="ev_share", color="country", markers=True,
                            title="EV share of new sales (%)"), use_container_width=True)
    show = c[c.country.isin(sel)].set_index("country")[
        ["archetype", "primary_segment", "target_share", "target_year", "target_note", "petrol_usd_l",
         "elec_usd_kwh", "grid_gco2_kwh", "oil_import_pct"]]
    def tidy(v):  # years and whole numbers without ".0"; blanks as a dash
        if v != v or v is None:
            return "-"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    st.dataframe(show.T.astype(object).apply(lambda col: col.map(tidy)), use_container_width=True)
    st.caption("Policy notes are stored seed values and may be outdated. Run the AI Analyst for current status.")
