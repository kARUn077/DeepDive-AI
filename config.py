import os
from dotenv import load_dotenv

def load_app_secrets() -> None:
    load_dotenv()

    try:
        import streamlit as st
    except Exception:
        return

    for key in ("MISTRAL_API_KEY", "TAVILY_API_KEY"):
        val = os.getenv(key)
        if (not val or val.strip() == "") and hasattr(st, "secrets") and key in st.secrets:
            os.environ[key] = str(st.secrets[key]).strip()
        elif val:
            os.environ[key] = val.strip()