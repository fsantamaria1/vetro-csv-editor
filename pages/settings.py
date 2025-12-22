"""
Settings page for the Vetro Feature Layer Editor.
Manages API key configuration using browser localStorage for security.
"""

import os
import streamlit as st
from decouple import config
from vetro.ui import render_sidebar

# Import custom storage helpers
from vetro import (
    load_key_from_local_storage,
    save_key_to_local_storage,
    delete_key_from_local_storage,
)

st.set_page_config(page_title="Settings - Vetro Editor", page_icon="⚙️", layout="wide")


def init_session_state():
    """Initialize session state defaults."""
    # Flag to force a storage re-check
    should_recheck_storage = False

    # 1. Check User API Key
    # If this is missing, it means we are either on a fresh load
    # OR we navigated back from another page (and Streamlit cleaned up the widget).
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""
        should_recheck_storage = True

    # 2. Check Key Preference
    if "key_preference" not in st.session_state:
        st.session_state.key_preference = "Use user key (if set)"
        should_recheck_storage = True

    # 3. Logic: If we had to restore missing keys, we MUST check storage again.
    if should_recheck_storage:
        st.session_state.storage_checked = False

    # 4. Default initialization for the flag itself
    if "storage_checked" not in st.session_state:
        st.session_state.storage_checked = False


def on_clear_key():
    """Callback: clear key from session and flag for JS deletion."""
    st.session_state.user_api_key = ""
    # We set a flag so the JS execution happens in the main body
    st.session_state.pending_delete = True


def on_key_change():
    """Callback: mark key as unsaved when user types."""
    st.session_state.saved_to_browser = False


def on_pref_change():
    """Callback: save preference immediately when changed."""
    save_key_to_local_storage(st.session_state.key_preference, "vetro_key_pref")


init_session_state()
render_sidebar()


def main():
    """Main execution function for the settings page."""
    st.title("⚙️ Settings")
    st.markdown("Configure your API connection and application preferences.")

    # ========== Auto-load logic ==========
    if not st.session_state.storage_checked:
        # Load both user settings items
        stored_key = load_key_from_local_storage("vetro_api_key")
        stored_pref = load_key_from_local_storage("vetro_key_pref")

        # Only proceed if BOTH have finished loading (are not None)
        if stored_key is not None and stored_pref is not None:
            if stored_key:
                st.session_state.user_api_key = stored_key
                st.session_state.saved_to_browser = True

            if stored_pref:
                st.session_state.key_preference = stored_pref

            st.session_state.storage_checked = True
            st.rerun()

    # ========== Pending Delete Logic ==========
    if st.session_state.get("pending_delete"):
        delete_key_from_local_storage("vetro_api_key")
        st.session_state.pending_delete = False
        st.toast("Key removed from browser storage.")

    left_col, right_col = st.columns([2, 1])

    with left_col:
        # ========== Backend Key Status ==========
        st.subheader("1. Backend Environment")
        backend_key = os.environ.get("VETRO_API_KEY", "") or config(
            "VETRO_API_KEY", default=""
        )

        if backend_key:
            st.success("✅ Backend API key is configured (hidden).")
            st.caption(
                "The server has a default key loaded from the environment variables."
            )
        else:
            st.warning("⚠️ No backend API key configured.")
            st.caption("You must provide a User Key below to interact with the API.")

        st.divider()

        # ========== User API Key ==========
        st.subheader("2. Your Session Key")
        st.markdown("Override the backend key with your personal API key.")

        st.text_input(
            "Enter Vetro API Key",
            key="user_api_key",
            type="password",
            on_change=on_key_change,
            help="Your key is stored securely in your browser's LocalStorage.",
            placeholder="Ex: Token 12345...",
        )

        col_save, col_clear = st.columns([1, 2])

        with col_save:
            if st.button("💾 Save Key", type="primary"):
                if st.session_state.user_api_key:
                    save_key_to_local_storage(
                        st.session_state.user_api_key, "vetro_api_key"
                    )
                    st.session_state.saved_to_browser = True
                    st.success("Key saved to browser!")
                else:
                    st.error("Enter a key first.")

        with col_clear:
            st.button("🗑️ Clear Key", on_click=on_clear_key)

        # Visual Feedback
        if st.session_state.user_api_key and st.session_state.saved_to_browser:
            current_key = st.session_state.user_api_key
            if len(current_key) > 8:
                masked = f"{current_key[:4]}...{current_key[-4:]}"
            else:
                masked = "••••"

            st.info(f"🔑 Active User Key: **{masked}** (Loaded from Browser Storage)")

    with right_col:
        # ========== Preferences ==========
        with st.container(border=True):
            st.subheader("Preferences")

            st.radio(
                "Priority Logic",
                options=["Use user key (if set)", "Always use backend key"],
                key="key_preference",
                on_change=on_pref_change,
                help="Decide which key takes precedence if both are available.",
            )

            st.markdown("---")

            pref = st.session_state.key_preference
            active_key = (
                backend_key
                if pref == "Always use backend key"
                else (st.session_state.user_api_key or backend_key)
            )

            st.markdown("**Status:**")
            if active_key:
                st.success("🟢 Ready to Connect")
            else:
                st.error("🔴 No Key Available")

    st.divider()

    with st.expander("ℹ️ Storage & Security Details"):
        st.markdown(
            """
        ### Data Privacy
        * **User Keys** are stored in your browser's **LocalStorage**.
        * **Backend Keys** are loaded from the server's environment variables or a `.env`.
        * Keys are **never** logged or saved to the server disk by this application.
        """
        )


if __name__ == "__main__":
    main()
