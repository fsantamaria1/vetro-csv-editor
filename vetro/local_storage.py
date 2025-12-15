"""
Simple helpers to sync API key between browser localStorage and Streamlit session state.
Uses json.dumps to safely serialize data for JavaScript execution.
"""

import json
from streamlit_js_eval import streamlit_js_eval as sje


def load_key_from_local_storage(local_key_name: str = "vetro_api_key") -> str:
    """
    Attempt to load the API key from browser localStorage.
    Returns the key if found, otherwise returns empty string.
    """
    try:
        safe_key_name = json.dumps(local_key_name)
        result = sje(
            js_expressions=f"localStorage.getItem({safe_key_name})",
            key=f"load_{local_key_name}",
        )
        if result is not None:
            return result if isinstance(result, str) else ""
    except (RuntimeError, ValueError, TypeError):
        pass
    return ""


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
