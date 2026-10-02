import os

def load_env():
    """Load .env locally and Streamlit secrets in the cloud into os.environ."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    try:
        import streamlit as st
        for k, v in st.secrets.items():
            if isinstance(v, str):
                os.environ.setdefault(k, v)
    except Exception:
        pass
