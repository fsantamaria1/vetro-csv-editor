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
