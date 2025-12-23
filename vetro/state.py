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
    # 1. Initialize Safety Vaults (These survive page navigation)
    if "_api_key_store" not in st.session_state:
        st.session_state._api_key_store = ""
    if "_pref_store" not in st.session_state:
        st.session_state._pref_store = "Use user key (if set)"

    # 2. Sync Vault -> Data Variable (The Source of Truth)
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = st.session_state._api_key_store

    if "key_preference" not in st.session_state:
        st.session_state.key_preference = st.session_state._pref_store

    # 3. Sync Data -> Widget Keys (The UI)
    # This creates the widget keys BEFORE the page renders, ensuring they aren't empty.
    st.session_state.widget_user_api_key = st.session_state.user_api_key
    st.session_state.widget_key_preference = st.session_state.key_preference

    # 4. Initialize Flags
    if "storage_checked" not in st.session_state:
        st.session_state.storage_checked = False

    if "loaded_from_storage" not in st.session_state:
        st.session_state.loaded_from_storage = False


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
                # Update Data, Vault, and Widget
                st.session_state.user_api_key = stored_key
                st.session_state._api_key_store = stored_key
                st.session_state.widget_user_api_key = stored_key
                st.session_state.loaded_from_storage = True

            if stored_pref:
                st.session_state.key_preference = stored_pref
                st.session_state._pref_store = stored_pref
                st.session_state.widget_key_preference = stored_pref

            st.session_state.storage_checked = True
            st.rerun()

    # 2. Pending Delete Logic
    if st.session_state.get("pending_delete"):
        delete_key_from_local_storage("vetro_api_key")
        st.session_state.pending_delete = False
        st.session_state._api_key_store = ""  # Clear Vault

        # Clear Data and Widget
        st.session_state.user_api_key = ""
        st.session_state.widget_user_api_key = ""

        st.toast("Key removed from browser storage.")


# ========== Callbacks ==========


def on_key_change():
    """Sync Widget -> Data Variable."""
    st.session_state.user_api_key = st.session_state.widget_user_api_key
    st.session_state._api_key_store = st.session_state.widget_user_api_key
    st.session_state.loaded_from_storage = False


def on_clear_key():
    """Clear key from session and flag for JS deletion."""
    st.session_state.user_api_key = ""
    st.session_state._api_key_store = ""
    st.session_state.widget_user_api_key = ""
    st.session_state.pending_delete = True


def on_pref_change():
    """Sync Widget -> Data Variable and Save."""
    st.session_state.key_preference = st.session_state.widget_key_preference
    st.session_state._pref_store = st.session_state.widget_key_preference
    save_key_to_local_storage(st.session_state.key_preference, "vetro_key_pref")
