# ⚡ EVSync Global

Multi-agent EV transition intelligence for any country: **policy, supply-chain risk, cost of ownership,
oil displacement and adoption forecasts**, with sourced, fact-checked briefings.

Built with **CrewAI + Streamlit + Plotly + SciPy**. Open source (MIT).

## Architecture
Streamlit pages (dashboards) + a CrewAI crew of 7 agents (researcher, policy, supply chain, economist,
forecaster, strategist, fact-checker). All numbers come from deterministic Python tools in `core/calc.py`;
agents call tools and interpret results, and the fact-checker rejects unsourced claims.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # add SERPER_API_KEY + an LLM key
python scripts/make_sample_data.py                       # seed data (already included)
streamlit run app.py
```
The app works **without API keys** (dashboards + offline briefing). Keys enable the live AI Analyst.

## Pages
| Page | What it does |
|---|---|
| `app.py` | Global dashboard (map, trajectories, oil saved) |
| 2 Supply Chain Map | Lithium/cobalt/nickel/graphite/cell concentration + HHI |
| 3 Country Compare | 2-4 countries: adoption, policy, prices |
| 4 TCO Calculator | Auto-filled local prices; 2W, 3W, car, bus |
| 5 Forecasts | S-curve with 10-90% band and target year |
| 6 AI Analyst | Multi-agent crew, live progress, cached, multilingual |
| 7 Oil Displacement | Barrels/day, import bill, CO2 vs electrification level |

## Real data (replace seed data)
1. Download IEA Global EV Data Explorer CSV to `data/raw/iea_ev.csv`.
2. `python scripts/build_data.py` (also pulls World Bank indicators).
3. Add OWID, Ember/Electricity Maps (grid), USGS (minerals), UN Comtrade (flows), Open Charge Map (chargers).

## Known limitations (be upfront with judges)
- Seed data is small and approximate; policy notes go stale. The AI Analyst re-checks policy live.
- The S-curve is fit on 6 points; low-adoption countries have wide uncertainty. Improve with analog countries and longer history.
- The oil model counts gasoline litres only and ignores refinery co-products and fleet turnover.

## Deploy
Streamlit Community Cloud: connect repo, main file `app.py`, add secrets (`SERPER_API_KEY`, `OPENAI_API_KEY`, ...).

## Team
Abrar Hussain (lead), Sakina Jabeen, Owais Ali, Ahmad Yousif, Ayesha Khan Afridi, Nida Khan
