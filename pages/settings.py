"""
Settings page for the Vetro Feature Layer Editor.
Manages API key configuration using browser localStorage for security.
"""

import streamlit as st
from vetro.ui import render_sidebar
from vetro.local_storage import save_key_to_local_storage
from vetro.config import get_backend_key

# Import our new state manager
from vetro.state import (
    init_shared_state,
    sync_storage,
    on_key_change,
    on_clear_key,
    on_pref_change,
)

st.set_page_config(page_title="Settings - Vetro Editor", page_icon="⚙️", layout="wide")

# Initialize and Sync
init_shared_state()
render_sidebar()


def main():
    """Main execution function for the settings page."""
    # Run the sync logic (Auto-load & Pending Deletes)
    sync_storage()

    st.title("⚙️ Settings")
    st.markdown("Configure your API connection and application preferences.")

    left_col, right_col = st.columns([2, 1])

    with left_col:
        # ========== Backend Key Status ==========
        st.subheader("1. Backend Environment")
        backend_key = get_backend_key()
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

        # Widget Key is decoupled from Data Key to prevent deletion on nav
        st.text_input(
            "Enter Vetro API Key",
            key="widget_user_api_key",
            type="password",
            on_change=on_key_change,
            help="Your key is stored securely in your browser's LocalStorage.",
            placeholder="Ex: Token 12345...",
        )

        col_save, col_clear = st.columns([1, 1])

        with col_save:
            if st.button("💾 Save Key", type="primary"):
                if st.session_state.user_api_key:
                    save_key_to_local_storage(
                        st.session_state.user_api_key, "vetro_api_key"
                    )
                    st.success("Key saved to browser!")
                else:
                    st.error("Enter a key first.")

        with col_clear:
            st.button("🗑️ Clear Key", on_click=on_clear_key)

        # Visual Feedback
        # Only show this if the key actually came from the browser storage
        if st.session_state.user_api_key and st.session_state.loaded_from_storage:
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

            # Determine index safely for the radio button
            pref_options = ["Use user key (if set)", "Always use backend key"]
            try:
                # We check the WIDGET key here to ensure consistency
                curr_val = st.session_state.get(
                    "widget_key_preference", pref_options[0]
                )
                curr_index = pref_options.index(curr_val)
            except ValueError:
                curr_index = 0

            st.radio(
                "Priority Logic",
                options=pref_options,
                key="widget_key_preference",
                index=curr_index,
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
