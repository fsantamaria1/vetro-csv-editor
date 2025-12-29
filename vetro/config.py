"""
Utility functions for loading backend and active API keys.
Centralizes all key‑retrieval logic for the Vetro Editor.
"""

import os
import streamlit as st
from decouple import config


def get_backend_key():
    """Returns the backend API key from secrets, env, or .env."""
    return (
        st.secrets.get("VETRO_API_KEY")
        or os.environ.get("VETRO_API_KEY")
        or config("VETRO_API_KEY", default="")
    )


def get_effective_api_key():
    """
    Determine which API key to use based on session preferences.
    Returns the actual key string or None.
    """
    backend_key = get_backend_key()
    pref = st.session_state.get("key_preference", "Use user key (if set)")
    user_key = st.session_state.get("user_api_key", "")

    if pref == "Always use backend key":
        return backend_key or (user_key or None)
    return user_key or backend_key or None
