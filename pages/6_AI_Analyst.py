import hmac
import json
import os
import threading
from datetime import date
from pathlib import Path
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

from core.briefing import offline_brief
from core.data import countries
from core.env import load_env
from core.translation import RTL_CSS, RTL_LANGUAGES

st.set_page_config(page_title="AI Analyst", page_icon="🤖", layout="wide")
load_env()

DAILY_LIMIT = int(os.getenv("DAILY_RUN_LIMIT", "20"))      # live runs per day, whole app
SESSION_LIMIT = int(os.getenv("SESSION_RUN_LIMIT", "3"))   # live runs per visitor session
JUDGE_CODE = os.getenv("JUDGE_CODE", "")                   # empty = local development, no code needed
CACHE = Path("data/cache")
CACHE.mkdir(parents=True, exist_ok=True)
USAGE = CACHE / f"usage_{date.today()}.json"


def md(text, rtl=False):
    """Show a briefing. Urdu and Arabic are drawn right-to-left, as they are written."""
    safe = text.replace("$", "\\$")  # stop Streamlit treating $...$ as LaTeX
    if rtl:
        st.markdown(RTL_CSS, unsafe_allow_html=True)
        with st.container(key="brief"):
            st.markdown(safe)
    else:
        st.markdown(safe)


def runs_today() -> int:
    try:
        return int(json.loads(USAGE.read_text()).get("runs", 0))
    except Exception:
        return 0


def count_run():
    USAGE.write_text(json.dumps({"runs": runs_today() + 1}))
    st.session_state["runs"] = st.session_state.get("runs", 0) + 1


st.title("🤖 Multi-agent AI Analyst")
st.caption("7 CrewAI agents research, calculate with tools, forecast, write and fact-check a sourced briefing.")

c = countries()
col1, col2, col3 = st.columns(3)
country = col1.selectbox("Country", c.country.tolist(), index=c.country.tolist().index("Pakistan"))
audience = col2.radio("Audience", ["Policymaker", "Investor", "Manufacturer"], horizontal=True)
language = col3.selectbox("Language", ["English", "Urdu", "French", "Spanish", "Arabic", "Chinese"])
iso3 = c[c.country == country].iso3.iloc[0]
rtl = language in RTL_LANGUAGES
f = CACHE / f"{iso3}_{audience}_{language}_{date.today()}.md"

keys_ok = bool(os.getenv("SERPER_API_KEY")) and any(
    os.getenv(k) for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"))

code_ok = True
if JUDGE_CODE:
    with st.expander("Judge and team access (live agent runs)"):
        entered = st.text_input("Access code", type="password")
    code_ok = hmac.compare_digest(entered.encode(), JUDGE_CODE.encode()) if entered else False

left_today = max(DAILY_LIMIT - runs_today(), 0)
left_session = max(SESSION_LIMIT - st.session_state.get("runs", 0), 0)
can_run = keys_ok and code_ok and left_today > 0 and left_session > 0

run = st.button("Run multi-agent analysis", type="primary", disabled=not can_run)
if not keys_ok:
    st.info("Live agents are not configured here. Saved briefings below are free to browse.")
elif not code_ok:
    st.info("Live runs need an access code (given to judges and the team). Saved briefings below are free to browse.")
elif left_today == 0 or left_session == 0:
    st.warning("Live-run limit reached for now. Saved briefings below are still available.")
else:
    st.caption(f"Live runs left: {min(left_today, left_session)} (limits protect the project's API budget).")

if run:
    if f.exists():
        st.success("Loaded today's cached briefing.")
        md(f.read_text(encoding="utf-8"), rtl)
    else:
        from agents.crew import EVSyncCrew  # imported lazily so the app starts without crewai keys
        count_run()
        lines, feed = [], st.empty()
        ctx = get_script_run_ctx()  # lets crew worker threads update this page safely

        def on_task(out):
            try:
                add_script_run_ctx(threading.current_thread(), ctx)
                lines.append(f"✅ **{getattr(out, 'agent', 'Agent')}** finished a task")
                feed.markdown("\n\n".join(lines))
            except Exception:
                pass  # a progress-display problem must never fail an agent task

        with st.status("Agents working...", expanded=True) as status:
            try:
                result = EVSyncCrew(on_task=on_task).crew().kickoff(
                    inputs={"country": country, "iso3": iso3, "audience": audience, "language": language,
                            "today": date.today().isoformat(), "year": str(date.today().year)})
                f.write_text(result.raw, encoding="utf-8")
                status.update(label="Analysis complete", state="complete")
                md(result.raw, rtl)
                st.download_button("Download briefing", result.raw, file_name=f"{iso3}_EV_brief.md")
            except Exception as e:
                status.update(label="Agent run failed, showing offline briefing", state="error")
                st.error(str(e))
                md(offline_brief(iso3, audience))
else:
    pre = Path("data/precached") / f"{iso3}_{audience}_{language}.md"
    if pre.exists():
        st.subheader("Saved agent briefing")
        st.caption("Generated by the agent crew and reviewed by the team. Press Run (with access) for a fresh analysis.")
        md(pre.read_text(encoding="utf-8"), rtl)
    else:
        st.subheader("Offline preview (no API needed)")
        md(offline_brief(iso3, audience))
