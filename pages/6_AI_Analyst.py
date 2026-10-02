import os
from datetime import date
from pathlib import Path
import streamlit as st

from core.briefing import offline_brief
from core.data import countries
from core.env import load_env

st.set_page_config(page_title="AI Analyst", page_icon="🤖", layout="wide")
load_env()


def md(text):
    st.markdown(text.replace("$", "\\$"))  # stop Streamlit treating $...$ as LaTeX


st.title("🤖 Multi-agent AI Analyst")
st.caption("7 CrewAI agents research, calculate with tools, forecast, write and fact-check a sourced briefing.")

c = countries()
col1, col2, col3 = st.columns(3)
country = col1.selectbox("Country", c.country.tolist(), index=c.country.tolist().index("Pakistan"))
audience = col2.radio("Audience", ["Policymaker", "Investor", "Manufacturer"], horizontal=True)
language = col3.selectbox("Language", ["English", "Urdu", "French", "Spanish", "Arabic", "Chinese"])
iso3 = c[c.country == country].iso3.iloc[0]

cache = Path("data/cache")
cache.mkdir(parents=True, exist_ok=True)
f = cache / f"{iso3}_{audience}_{language}_{date.today()}.md"
keys_ok = bool(os.getenv("SERPER_API_KEY")) and any(
    os.getenv(k) for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"))

run = st.button("Run multi-agent analysis", type="primary", disabled=not keys_ok)
if not keys_ok:
    st.info("Add SERPER_API_KEY and an LLM key in .env or Streamlit secrets to enable live agents. "
            "Offline preview below uses deterministic tools only.")

if run:
    if f.exists():
        st.success("Loaded today's cached briefing.")
        md(f.read_text())
    else:
        from agents.crew import EVSyncCrew  # imported lazily so the app starts without crewai keys
        lines, feed = [], st.empty()

        def on_task(out):
            lines.append(f"✅ **{getattr(out, 'agent', 'Agent')}** finished a task")
            feed.markdown("\n\n".join(lines))

        with st.status("Agents working...", expanded=True) as status:
            try:
                result = EVSyncCrew(on_task=on_task).crew().kickoff(
                    inputs={"country": country, "iso3": iso3, "audience": audience, "language": language,
                            "today": date.today().isoformat(), "year": str(date.today().year)})
                f.write_text(result.raw)
                status.update(label="Analysis complete", state="complete")
                md(result.raw)
                st.download_button("Download briefing", result.raw, file_name=f"{iso3}_EV_brief.md")
            except Exception as e:
                status.update(label="Agent run failed, showing offline briefing", state="error")
                st.error(str(e))
                md(offline_brief(iso3, audience))
else:
    pre = Path("data/precached") / f"{iso3}_{audience}_{language}.md"
    if pre.exists():
        st.subheader("Saved agent briefing")
        st.caption(f"Pre-computed by the crew on {date.fromtimestamp(pre.stat().st_mtime)}. "
                   "Press Run for a fresh live analysis.")
        md(pre.read_text())
    else:
        st.subheader("Offline preview (no API needed)")
        md(offline_brief(iso3, audience))
