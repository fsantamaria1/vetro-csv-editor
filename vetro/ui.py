"""
Shared UI components using native Streamlit elements.
"""

import os
import streamlit as st
from decouple import config


def render_sidebar():
    """
    Renders the consistent sidebar elements:
    - Logo (Native st.logo)
    - Status Indicator (Native container with colored markdown)
    - Resource Links (Native st.link_button)
    """
    # 1. Native Logo
    st.logo(
        "https://cdn-icons-png.flaticon.com/512/6062/6062646.png",
        icon_image="https://cdn-icons-png.flaticon.com/512/6062/6062646.png",
        size="large",
    )

    with st.sidebar:
        st.divider()

        # 2. Status Widget (Using native border container)
        backend_key = os.environ.get("VETRO_API_KEY") or config(
            "VETRO_API_KEY", default=""
        )
        user_key = st.session_state.get("user_api_key")

        st.subheader("🔌 Connection")

        with st.container(border=True):
            if user_key or backend_key:
                st.markdown("**:green[● Online]**")

                if user_key:
                    st.caption("Using: **Session Key**")
                else:
                    st.caption("Using: **Backend Key**")
            else:
                st.markdown("**:red[● Offline]**")
                st.caption("Please configure settings")

        st.divider()

        # 3. Resources (Using native link buttons)
        st.subheader("📚 Resources")

        # These render as clean, clickable buttons that open in a new tab
        st.link_button(
            "📖 API Documentation",
            "https://app.vetro.io/integrations/list/guides",
            width="stretch",
        )

        st.link_button(
            "🐞 Report an Issue",
            "https://github.com/fsantamaria1/vetro-csv-editor/issues",
            width="stretch",
            help="Found a bug? Let us know on GitHub.",
        )

        st.divider()
        st.caption("Vetro Editor v1.0.0")
