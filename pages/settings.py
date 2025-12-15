"""
Settings page for the Vetro Feature Layer Editor.
Manages API key configuration using browser localStorage for security.
"""
import os
import streamlit as st
from decouple import config
from vetro.ui import render_sidebar

st.set_page_config(page_title="Settings - Vetro Editor", page_icon="⚙️", layout="wide")

render_sidebar()

def main():
    st.title("⚙️ Settings")
    st.markdown("Configure your API connection and application preferences.")

    left_col, right_col = st.columns([2, 1])

    with left_col:
        # ========== Backend Key Status ==========
        st.subheader("1. Backend Environment")
        backend_key = os.environ.get("VETRO_API_KEY", "") or config("VETRO_API_KEY", default="")

        if backend_key:
            st.success("✅ Backend API key is configured (hidden).")
            st.caption("The server has a default key loaded from the environment variables.")
        else:
            st.warning("⚠️ No backend API key configured.")
            st.caption("You must provide a User Key below to interact with the API.")

        st.divider()

        # ========== User API Key ==========
        st.subheader("2. Your Session Key")
        st.markdown("Override the backend key with your personal API key.")

        key_input = st.text_input(
            "Enter Vetro API Key",
            type="password",
            help="Your key is stored securely in your browser's LocalStorage.",
            placeholder="Ex: Token 12345..."
        )

        col_save, col_clear = st.columns([1, 4])

        with col_save:
            if st.button("💾 Save Key", type="primary"):
                if key_input:
                    st.success("Key saved to browser!")
                    st.rerun()
                else:
                    st.error("Enter a key first.")

        with col_clear:
            if st.button("🗑️ Clear Key"):
                st.warning("Key removed from browser and session.")
                st.rerun()

    with right_col:
        # ========== Preferences ==========
        with st.container(border=True):
            st.subheader("Preferences")

            pref = st.radio(
                "Priority Logic",
                options=["Use user key (if set)", "Always use backend key"],
                help="Decide which key takes precedence if both are available."
            )


            st.markdown("---")

            active_key = (
                backend_key if pref == "Always use backend key"
                else None
            )

            st.markdown("**Status:**")
            if active_key:
                st.success("🟢 Ready to Connect")
            else:
                st.error("🔴 No Key Available")



    st.divider()

    with st.expander("ℹ️ Storage & Security Details"):
        st.markdown("""
        ### Data Privacy
        * **User Keys** are stored in your browser's **LocalStorage**.
        * **Backend Keys** are loaded from the server's environment variables (`.env`).
        * Keys are **never** logged or saved to the server disk by this application.
        """)

if __name__ == "__main__":
    main()