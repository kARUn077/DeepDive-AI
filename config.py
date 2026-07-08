import os

from dotenv import load_dotenv


def load_app_secrets() -> None:
    load_dotenv()

    try:
        import streamlit as st
    except Exception:
        return

    for key in ("MISTRAL_API_KEY", "TAVILY_API_KEY"):
        if not os.getenv(key) and key in st.secrets:
            os.environ[key] = str(st.secrets[key])