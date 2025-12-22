"""
Simple helpers to sync API key between browser localStorage and Streamlit session state.
Uses json.dumps to safely serialize data for JavaScript execution.
"""

import json
from typing import Optional
from streamlit_js_eval import streamlit_js_eval as sje


def load_key_from_local_storage(local_key_name: str = "vetro_api_key") -> Optional[str]:
    """
    Attempt to load the API key from browser localStorage.

    Returns:
        - None: If the component is still loading (WAIT).
        - "": If the key is not found or empty.
        - str: The actual key.
    """
    try:
        safe_key_name = json.dumps(local_key_name)
        # We use || '' to ensure we get an empty string if the key is missing (null),
        # allowing us to distinguish 'Missing' from 'Still Loading' (None).
        result = sje(
            js_expressions=f"localStorage.getItem({safe_key_name}) || ''",
            key=f"load_{local_key_name}",
        )
        # If result is None, the component hasn't reported back yet.
        return result
    except (RuntimeError, ValueError, TypeError):
        pass
    return None


def save_key_to_local_storage(
    api_key: str, local_key_name: str = "vetro_api_key"
) -> None:
    """
    Save the API key to browser localStorage.
    """
    try:
        safe_key = json.dumps(api_key)
        safe_key_name = json.dumps(local_key_name)

        sje(
            js_expressions=f"localStorage.setItem({safe_key_name}, {safe_key})",
            key=f"save_{local_key_name}",
        )
    except (RuntimeError, ValueError, TypeError):
        pass


def delete_key_from_local_storage(local_key_name: str = "vetro_api_key") -> None:
    """
    Delete the API key from browser localStorage.
    """
    try:
        safe_key_name = json.dumps(local_key_name)
        sje(
            js_expressions=f"localStorage.removeItem({safe_key_name})",
            key=f"delete_{local_key_name}",
        )
    except (RuntimeError, ValueError, TypeError):
        pass
