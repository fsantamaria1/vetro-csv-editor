"""
State management for Vetro Editor.
Handles session initialization, callbacks, and browser storage synchronization.
"""

import streamlit as st
from vetro.local_storage import (
    load_key_from_local_storage,
    save_key_to_local_storage,
    delete_key_from_local_storage,
)


def init_session_state():
    """
    Ensure all required session state variables exist.
    Should be called at the top of every page.
    """
    should_recheck_storage = False

    # 1. User API Key
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""
        should_recheck_storage = True

    # 2. Key Preference
    if "key_preference" not in st.session_state:
        st.session_state.key_preference = "Use user key (if set)"
        should_recheck_storage = True

    # 3. Storage Checked Flag
    if "storage_checked" not in st.session_state:
        st.session_state.storage_checked = False
    elif should_recheck_storage:
        # If we restored missing keys, force a re-check
        st.session_state.storage_checked = False


def sync_storage():
    """
    Execute storage synchronization logic:
    1. Auto-load keys from browser if not checked yet.
    2. Process pending deletions.
    """
    # 1. Auto-load Logic
    if not st.session_state.storage_checked:
        stored_key = load_key_from_local_storage("vetro_api_key")
        stored_pref = load_key_from_local_storage("vetro_key_pref")

        if stored_key is not None and stored_pref is not None:
            if stored_key:
                st.session_state.user_api_key = stored_key
                st.session_state.loaded_from_storage = True

            if stored_pref:
                st.session_state.key_preference = stored_pref

            st.session_state.storage_checked = True
            st.rerun()

    # 2. Pending Delete Logic
    if st.session_state.get("pending_delete"):
        delete_key_from_local_storage("vetro_api_key")
        st.session_state.pending_delete = False
        st.toast("Key removed from browser storage.")


# ========== Callbacks ==========


def on_key_change():
    """Reset loaded flag when user types in the input box."""
    st.session_state.loaded_from_storage = False


def on_clear_key():
    """Clear key from session and flag for JS deletion."""
    st.session_state.user_api_key = ""
    st.session_state.pending_delete = True


def on_pref_change():
    """Save preference immediately when changed."""
    save_key_to_local_storage(st.session_state.key_preference, "vetro_key_pref")
