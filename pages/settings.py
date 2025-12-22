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
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""
    if "key_preference" not in st.session_state:
        st.session_state.key_preference = "Use user key (if set)"

    # Track if we have already checked storage this session
    if "storage_checked" not in st.session_state:
        st.session_state.storage_checked = False


init_session_state()
render_sidebar()


def main():
    """Main execution function for the settings page."""
    st.title("⚙️ Settings")
    st.markdown("Configure your API connection and application preferences.")

    if not st.session_state.storage_checked:
        # Load both user settings items
        stored_key = load_key_from_local_storage("vetro_api_key")
        stored_pref = load_key_from_local_storage("vetro_key_pref")

        # Only proceed if BOTH have finished loading (are not None)
        if stored_key is not None and stored_pref is not None:
            if stored_key:
                st.session_state.user_api_key = stored_key

            if stored_pref:
                st.session_state.key_preference = stored_pref

            st.session_state.storage_checked = True
            st.rerun()

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

        key_input = st.text_input(
            "Enter Vetro API Key",
            value=st.session_state.user_api_key,
            type="password",
            help="Your key is stored securely in your browser's LocalStorage.",
            placeholder="Ex: Token 12345...",
        )

        col_save, col_clear = st.columns([1, 2])

        with col_save:
            if st.button("💾 Save Key", type="primary"):
                if key_input:
                    st.session_state.user_api_key = key_input
                    save_key_to_local_storage(key_input, "vetro_api_key")
                    st.success("Key saved to browser!")
                    # NOTE: We DO NOT rerun here, let the save JS execute.
                else:
                    st.error("Enter a key first.")

        with col_clear:
            if st.session_state.user_api_key:
                if st.button("🗑️ Clear Key"):
                    st.session_state.user_api_key = ""
                    delete_key_from_local_storage("vetro_api_key")
                    st.warning("Key removed from browser and session.")
                    # NOTE: We DO NOT rerun here either, let the delete JS execute.

        # Visual Feedback
        if st.session_state.user_api_key:
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

            # Determine index for radio based on current state
            current_pref_index = 0
            if st.session_state.key_preference == "Always use backend key":
                current_pref_index = 1

            pref = st.radio(
                "Priority Logic",
                options=["Use user key (if set)", "Always use backend key"],
                index=current_pref_index,
                help="Decide which key takes precedence if both are available.",
            )

            # Update state AND save to storage if changed
            if pref != st.session_state.key_preference:
                st.session_state.key_preference = pref
                save_key_to_local_storage(pref, "vetro_key_pref")
                st.success("Preference saved.")

            st.markdown("---")

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
