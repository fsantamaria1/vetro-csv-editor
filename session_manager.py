"""
session_manager.py
Centralized management for Streamlit session state initialization.
"""
import streamlit as st

def init_session_state():
    """
    Initialize all shared session state keys for the application.
    Using setdefault ensures we don't overwrite existing data on reruns.
    """
    # --- Core Data ---
    st.session_state.setdefault("dataframes", {})
    st.session_state.setdefault("feature_types", {})
    st.session_state.setdefault("current_file", None)

    # --- API & Authentication ---
    st.session_state.setdefault("user_api_key", "")
    st.session_state.setdefault("key_preference", "Use user key (if set)")
    
    # --- UI & State Tracking ---
    # Used in Settings to ensure we only load from local storage once per session
    st.session_state.setdefault("storage_checked", False)
    
    # Used in Editor to force-reset the data_editor widget when needed
    st.session_state.setdefault("editor_id", 0)
