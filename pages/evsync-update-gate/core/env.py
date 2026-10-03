import os


def load_env():
    """Load .env locally and Streamlit secrets in the cloud into os.environ."""
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")  # no interactive trace prompt
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")        # no telemetry
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    try:
        import streamlit as st
        for k, v in st.secrets.items():
            if isinstance(v, (str, int, float)):
                os.environ.setdefault(k, str(v))
    except Exception:
        pass
