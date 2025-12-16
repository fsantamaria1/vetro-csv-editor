"""
Root page for the Vetro Feature Layer Editor app.
This serves as the Home/Welcome screen.
"""

import os
import streamlit as st
from decouple import config
from vetro.ui import render_sidebar
from session_manager import init_session_state

st.set_page_config(
    page_title="Vetro Feature Layer Editor", page_icon="🔧", layout="wide"
)

init_session_state()
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

        **Use the sidebar to navigate:**
        - **Editor** — Upload CSV files and edit feature properties
        - **Settings** — Manage your API key and preferences
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
        st.warning(
            "No backend  API key configured on the server. "
            "Use Settings to save your personal key to the browser."
        )

    st.divider()

    st.markdown("### 📋 Supported Feature Types")
    st.markdown(
        """
    - 🌸 **Flower Pot Dead End** — ID, Location, Name, Notes, Size, Type, RUS Code
    - 📍 **Service Location** — ID, Name, Address, City, State, Zip Code, Location Type
    - 🕳️ **Handhole** — ID, Name, Location, Type, Size, Owner, Build
    - 🔗 **Aerial Splice Closure** — ID, Name, Owner, Location, Links, Structure ID
    - 🚩 **Pole ** - ID, Road Name, Town, Project, State, Owner, Elco Id, Telco Id, Drop Type, Status, Make Ready Required, Licensed, Attachment Height, Age, Class, Diameter, Height, Links, Make Ready LoE, Material, Permitted, Surveyed, Type, Latitude, Survey Date, Longitude, Make Ready Explanation, Assigned To, Permit Number
    """
    )

    st.divider()

    st.markdown("### 🚀 Quick Start")
    st.markdown(
        """
    1. Go to **Settings** and set up your API key (or use backend key if configured)
    2. Go to **Editor** and upload a CSV file
    3. Edit properties inline (Excel-like editing with drag-fill)
    4. Review changes and confirm before sending to Vetro API
    5. Export your edited data
    """
    )

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
