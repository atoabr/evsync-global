import streamlit as st
from core import calc
from core.data import countries

st.set_page_config(page_title="TCO", page_icon="💰", layout="wide")
st.title("💰 Total cost of ownership: EV vs petrol")
c = countries().set_index("country")
country = st.selectbox("Country (auto-fills local prices)", c.index.tolist(), index=list(c.index).index("Pakistan"))
vt = st.radio("Vehicle", list(calc.VEHICLES), horizontal=True, index=2)
d, r = calc.VEHICLES[vt], c.loc[country]

a, b, e = st.columns(3)
price_ev = a.number_input("EV price (USD)", value=float(d["price_ev"]))
price_ice = a.number_input("Petrol vehicle price (USD)", value=float(d["price_ice"]))
km = b.number_input("km per year", value=float(d["km_year"]))
years = b.slider("Years owned", 3, 15, 8)
elec = e.number_input("Electricity USD/kWh", value=float(r.elec_usd_kwh), format="%.3f")
fuel = e.number_input("Fuel USD/litre", value=float(r.petrol_usd_l), format="%.2f")
subsidy = st.number_input("Purchase subsidy (USD)", value=0.0)
res = calc.tco(price_ev, price_ice, km, elec, fuel, d["kwh_100"], d["l_100"], years, subsidy=subsidy)

m1, m2, m3, m4 = st.columns(4)
m1.metric("EV total", f"${res['ev_total']:,}")
m2.metric("Petrol total", f"${res['ice_total']:,}")
m3.metric("EV savings", f"${res['savings']:,}")
m4.metric("Breakeven", "never" if res["breakeven_years"] is None else f"{res['breakeven_years']} yrs")
st.caption("Bus uses the petrol price as a diesel proxy. Maintenance assumed 2% (EV) / 4% (ICE) of price per year.")
