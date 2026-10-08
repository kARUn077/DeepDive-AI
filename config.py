import os
from dotenv import load_dotenv

def load_app_secrets() -> None:
    load_dotenv()

    try:
        import streamlit as st
    except Exception:
        return

    keys = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY", "TAVILY_API_KEY", "MISTRAL_API_KEY")
    for key in keys:
        val = os.getenv(key)
        if (not val or val.strip() == "") and hasattr(st, "secrets") and key in st.secrets:
            os.environ[key] = str(st.secrets[key]).strip()
        elif val:
            os.environ[key] = val.strip()

    # Alias GOOGLE_API_KEY / GEMINI_API_KEY so both work seamlessly
    gemini_k = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_k:
        os.environ["GEMINI_API_KEY"] = gemini_k
        os.environ["GOOGLE_API_KEY"] = gemini_k

