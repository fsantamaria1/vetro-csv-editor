"""
Root page for the Vetro Feature Layer Editor app.
This servers as the Home/Welcome screen.
"""
import os
import streamlit as st
from decouple import config

st.set_page_config(
    page_title="Vetro Feature Layer Editor", page_icon="🔧", layout="wide"
)


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
        st.caption(
            "This does not expose the key. "
        )
    else:
        st.warning(
            "No backend  API key configured on the server. "
        )

    st.divider()

if __name__ == "__main__":
    main()