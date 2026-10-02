"""Creates SMALL ILLUSTRATIVE seed datasets so the app runs offline.
Values are rounded approximations for demo purposes. Replace/refresh them with
scripts/build_data.py (IEA / World Bank) and verify against primary sources."""
from pathlib import Path
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
YEARS = [2019, 2020, 2021, 2022, 2023, 2024]

# iso3, petrol $/L, elec $/kWh, grid gCO2/kWh, oil import %, vehicles (M), segment,
# target %, target year, target note, archetype, EV new-sales share history 2019-2024
C = {
 "Norway": ("NOR",1.9,0.15,30,0,3.2,"Cars",100,2025,"100% zero-emission new cars (national goal)","Oil exporter / EV leader",[42,75,86,86,82,89]),
 "China": ("CHN",1.1,0.09,550,72,340,"Cars + 2/3-wheelers",None,None,"NEV market share goals; already exceeding earlier targets","Manufacturing & refining superpower",[5,6,16,22,29,35]),
 "Germany": ("DEU",1.9,0.35,350,98,49,"Cars",100,2035,"EU 100% CO2-free new cars 2035 (under review; verify)","Import-dependent mature market",[3,14,26,31,24,20]),
 "United Kingdom": ("GBR",1.9,0.33,200,60,36,"Cars",100,2035,"ZEV mandate: 28% of new cars 2025, 33% 2026, 38% 2027, rising to 100% by 2035 (verify current status)","Import-dependent mature market",[1.6,10.7,11.6,16.6,16.5,19.6]),
 "United States": ("USA",0.95,0.17,370,0,280,"Cars + light trucks",None,None,"No binding federal target; state programs vary","Oil producer / large market",[2,2,4,6,9,10]),
 "Canada": ("CAN",1.3,0.11,120,0,26,"Cars + light trucks",100,2035,"ZEV mandate 100% by 2035; interim targets under federal review (verify)","Mineral producer / mature market",[3,4,5,7,9,12]),
 "India": ("IND",1.2,0.09,700,87,300,"2/3-wheelers",30,2030,"30% EV sales by 2030 (aspirational)","High-growth 2/3W market",[0.3,0.4,0.6,1.3,2,2.5]),
 "Pakistan": ("PAK",1.0,0.15,400,85,30,"2/3-wheelers",30,2030,"NEV Policy 2025-30: 30% of new vehicle sales electric by 2030; ~EUR 30M subsidies for ~116,000 e-motorcycles and ~3,200 e-rickshaws; 3,000 charging stations targeted by 2030 (verify). History = e-2W share of new two-wheeler sales (approx.)","High-growth 2/3W market",[0.0,0.0,0.05,0.15,0.5,2.2]),
 "Indonesia": ("IDN",0.8,0.10,680,45,150,"2/3-wheelers",None,None,"EV roadmap incl. e-2W and local nickel-to-battery chain","Mineral producer / 2W market",[0.1,0.2,0.5,1,1.7,2.5]),
 "Brazil": ("BRA",1.2,0.15,100,10,65,"Cars",None,None,"Biofuel-rich market; EV incentives evolving","Emerging biofuel-rich market",[0.3,0.4,0.6,1.2,2.5,4]),
 "Chile": ("CHL",1.4,0.17,300,95,5.5,"Cars + buses",100,2035,"100% light-duty EV sales by 2035; large e-bus fleet","Mineral producer / import-dependent",[0.1,0.2,0.4,0.8,1.5,2.5]),
 "Vietnam": ("VNM",1.0,0.08,500,60,75,"2/3-wheelers",None,None,"Domestic EV maker driving rapid growth","Emerging manufacturer / 2W market",[0.1,0.1,0.3,1,4,12]),
 "South Africa": ("ZAF",1.2,0.11,750,70,12,"Cars",None,None,"EV policy framework in development","Emerging import-dependent",[0.1,0.1,0.2,0.3,0.4,0.6]),
 "Australia": ("AUS",1.1,0.25,500,90,21,"Cars",None,None,"Vehicle emissions standard (NVES) in force","Mineral producer / mature market",[0.7,1,2,4,9,10]),
 "Japan": ("JPN",1.1,0.25,450,99,78,"Cars",100,2035,"100% electrified (incl. hybrids) new cars by 2035","Import-dependent mature market",[0.5,0.9,1,1.7,2.2,2.5]),
 "Ethiopia": ("ETH",0.8,0.03,25,100,1.5,"Cars",100,2024,"Ban on ICE car imports (2024)","Hydro-powered ICE-ban pioneer",[0,0,0.1,0.3,1,2]),
}
cols = ["country","iso3","petrol_usd_l","elec_usd_kwh","grid_gco2_kwh","oil_import_pct",
        "vehicles_millions","primary_segment","target_share","target_year","target_note","archetype"]
rows, hist = [], []
for name, v in C.items():
    rows.append([name, *v[:11]])
    for y, s in zip(YEARS, v[11]):
        hist.append([name, v[0], y, s])
pd.DataFrame(rows, columns=cols).to_csv(OUT/"countries.csv", index=False)
pd.DataFrame(hist, columns=["country","iso3","year","ev_share"]).to_csv(OUT/"ev_share_history.csv", index=False)

M = [  # mineral, stage, country, iso3, share %  (approximate, ~2023; verify with USGS / IEA)
 *[("Lithium","Mining",c,i,s) for c,i,s in [("Australia","AUS",47),("Chile","CHL",24),("China","CHN",15),("Argentina","ARG",6),("Other","OTH",8)]],
 *[("Lithium","Refining",c,i,s) for c,i,s in [("China","CHN",65),("Chile","CHL",20),("Argentina","ARG",5),("Other","OTH",10)]],
 *[("Cobalt","Mining",c,i,s) for c,i,s in [("DR Congo","COD",74),("Indonesia","IDN",7),("Other","OTH",19)]],
 *[("Cobalt","Refining",c,i,s) for c,i,s in [("China","CHN",76),("Finland","FIN",8),("Other","OTH",16)]],
 *[("Nickel","Mining",c,i,s) for c,i,s in [("Indonesia","IDN",50),("Philippines","PHL",10),("Other","OTH",40)]],
 *[("Nickel","Refining",c,i,s) for c,i,s in [("Indonesia","IDN",42),("China","CHN",30),("Other","OTH",28)]],
 *[("Graphite","Mining",c,i,s) for c,i,s in [("China","CHN",77),("Other","OTH",23)]],
 *[("Graphite","Refining",c,i,s) for c,i,s in [("China","CHN",90),("Other","OTH",10)]],
 *[("Battery cells","Manufacturing",c,i,s) for c,i,s in [("China","CHN",75),("South Korea","KOR",10),("Japan","JPN",5),("Other","OTH",10)]],
]
pd.DataFrame(M, columns=["mineral","stage","country","iso3","share_pct"]).to_csv(OUT/"minerals.csv", index=False)
print("sample data written to", OUT)
