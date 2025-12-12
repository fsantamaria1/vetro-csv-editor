"""
Root page for the Vetro Feature Layer Editor app.
This servers as the Home/Welcome screen.
"""

import os
import streamlit as st
from decouple import config
from vetro.ui import render_sidebar

st.set_page_config(
    page_title="Vetro Feature Layer Editor", page_icon="🔧", layout="wide"
)

render_sidebar()


def main():
    """
    Main entry point for the Vetro Feature Layer Editor application.
    Displays the welcome screen, navigation instructions, and security best practices.
    """
    st.markdown("# 🔧 :blue[Vetro Feature Layer Editor]")

    st.write(
        """
        Welcome to the Vetro Feature Layer Editor.
        """
    )

    # Check if backend API key is configured
    backend_key = os.environ.get("VETRO_API_KEY", "") or config(
        "VETRO_API_KEY", default=""
    )

    if backend_key:
        st.success("✅ Backend API key available (hidden).")
        st.caption("This does not expose the key. ")
    else:
        st.warning("No backend  API key configured on the server. ")

    st.divider()

    st.markdown("### 🔒 Security & Best Practices")
    st.markdown(
        """
    - 🔐 API keys are never printed or stored on the server by default
    - 🗝️ Use browser localStorage (encrypted) to persist your personal key
    - 👤 Use personal tokens for testing; integration tokens for production
    - 🗑️ Clear your key when done on a shared/public server
    """
    )


if __name__ == "__main__":
    main()
