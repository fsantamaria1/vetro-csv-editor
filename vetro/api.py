"""
Vetro API client encapsulating PATCH calls, retries/backoff, and helpers to convert
Pandas DataFrames to Vetro feature payloads.
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import requests
import pandas as pd
import streamlit as st

# Configure logger
logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

ALLOWED_LAYERS = [
    "Pole",
    "Handhole",
    "Service Location",
    "Aerial Splice Closure",
    "Flower Pot Dead End",
]

SYSTEM_FIELDS = [
    "layer_id",
    "plan_id",
    "global_id",
    "created_at",
    "updated_at",
    "geometry",
    "shape",
    "objectid",
    "external_id",
    "import_id",
]


class VetroAPIClient:
    """
    Client for Vetro API.

    - Uses exponential backoff for retrying transient errors (including 429).
    - Implements client-side throttling to prevent burst rate limit exhaustion.
    - Separates data conversion for easy unit testing.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.vetro.io/v3",
        request_timeout: int = 20,
        max_retries: int = 3,
        initial_backoff: float = 1.5,
        delay_between_batches: float = 1.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "Token": api_key,
        }
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.delay_between_batches = delay_between_batches

    def update_features(self, features: List[Dict]) -> Dict:
        """
        Call PATCH /features with features payload. Retries on 429/5xx using
        exponential backoff up to max_retries.
        """
        url = f"{self.base_url}/features"
        payload = {"features": features}
        attempt = 0
        backoff = self.initial_backoff

        while attempt <= self.max_retries:
            try:
                resp = requests.patch(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.request_timeout,
                )
                status = resp.status_code

                if status == 200:
                    try:
                        data = resp.json()
                    except ValueError:
                        data = resp.text
                    return {"success": True, "data": data, "status_code": status}

                if status == 429:
                    # Rate limited
                    logger.warning("Received 429 Too Many Requests from Vetro API.")
                    attempt += 1
                    if attempt > self.max_retries:
                        return {
                            "success": False,
                            "error": "Rate limit exceeded and retry limit reached.",
                            "status_code": status,
                            "rate_limited": True,
                        }
                    logger.info(
                        "Backing off for %.1fs (attempt %d/%d)",
                        backoff,
                        attempt,
                        self.max_retries,
                    )
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                if 500 <= status < 600:
                    # Server error
                    logger.warning("Server error %s from Vetro API.", status)
                    attempt += 1
                    if attempt > self.max_retries:
                        return {
                            "success": False,
                            "error": f"Server error {status}. Retry limit reached.",
                            "status_code": status,
                            "rate_limited": False,
                        }
                    logger.info(
                        "Backing off for %.1fs (attempt %d/%d)",
                        backoff,
                        attempt,
                        self.max_retries,
                    )
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                # Client error (400/401/etc.) - do not retry
                try:
                    err_body = resp.json()
                except ValueError:
                    err_body = resp.text
                return {
                    "success": False,
                    "error": f"HTTP {status}: {err_body}",
                    "status_code": status,
                    "rate_limited": False,
                }

            except requests.exceptions.RequestException as e:
                # Network or timeout -> retry
                logger.exception("RequestException calling Vetro API")
                attempt += 1
                if attempt > self.max_retries:
                    return {
                        "success": False,
                        "error": str(e),
                        "status_code": None,
                        "rate_limited": False,
                    }
                logger.info("Backing off for %.1fs after exception", backoff)
                time.sleep(backoff)
                backoff *= 2

        return {
            "success": False,
            "error": "Unknown failure",
            "status_code": None,
            "rate_limited": False,
        }

    def batch_update_features(
        self, df: pd.DataFrame, batch_size: int = 10, progress_callback=None
    ) -> Dict:
        """
        Split DataFrame into batches and call update_features for each.
        Includes a delay between batches to respect server rate limits.
        """
        total_rows = len(df)
        results = {
            "total": total_rows,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "rate_limited": False,
        }

        if "vetro_id" in df.columns:
            df = df[df["vetro_id"].notna()].copy()
        else:
            results["errors"].append({"error": "DataFrame missing 'vetro_id' column"})
            return results

        n = len(df)
        if n == 0:
            return results

        for start in range(0, n, batch_size):
            batch = df.iloc[start : start + batch_size]
            features = self.convert_df_to_features(batch)
            resp = self.update_features(features)

            if resp.get("success"):
                results["successful"] += len(batch)

                # Sleep after a success to let the bucket refill
                if (start + batch_size) < n:
                    time.sleep(self.delay_between_batches)

            else:
                results["failed"] += len(batch)
                results["errors"].append(
                    {"batch": start // batch_size + 1, "error": resp.get("error")}
                )
                if resp.get("rate_limited"):
                    results["rate_limited"] = True
                    break

            if progress_callback:
                progress_callback(min((start + batch_size) / n, 1.0), results)

        return results

    def convert_df_to_features(self, df: pd.DataFrame) -> List[Dict]:
        """Convert DataFrame to Vetro JSON payload, preserving types."""
        features = []
        for _, row in df.iterrows():
            properties = {}
            for col in df.columns:
                if col == "vetro_id" or str(col).startswith("v_"):
                    continue
                val = row[col]

                # 1. Explicit None -> JSON null
                if val is None:
                    properties[col] = None

                # 2. Valid data -> Check type
                elif pd.notna(val):
                    # If it is already a valid JSON primitive, send as-is
                    if isinstance(val, (int, float, bool)):
                        properties[col] = val
                    # Otherwise, safe string conversion
                    else:
                        properties[col] = str(val)

            vetro_id = row.get("vetro_id")
            feature = {
                "type": "Feature",
                "x-vetro": {"vetro_id": vetro_id},
                "properties": properties,
            }
            features.append(feature)
        return features


def map_vetro_type_to_python(
    html_type: str, permitted_values: Optional[List[Any]] = None
) -> str:
    """Translates Vetro HTML input types to our internal Editor types."""
    if html_type == "checkbox":
        return "bool"

    is_numeric_input = html_type == "number"

    if permitted_values and isinstance(permitted_values, list):
        if all(isinstance(v, int) for v in permitted_values):
            return "int"
        if all(isinstance(v, (int, float)) for v in permitted_values):
            return "float"

    if is_numeric_input:
        return "float"

    return "str"


def _parse_layer_attributes(
    attributes: Dict[str, Any],
) -> Tuple[List[str], Dict[str, str]]:
    """
    Helper to parse attributes for a single layer.
    Extracting this logic fixes the 'Too many local variables' linting error.
    """
    columns = []
    type_overrides = {}

    for name, attr in attributes.items():
        if attr.get("is_hidden", False):
            continue
        if name.lower() in SYSTEM_FIELDS or name.startswith("v_"):
            continue

        columns.append(name)

        html_input = attr.get("html_input_type", "text")
        permitted = attr.get("permitted_values")

        # Call our clean mapping function
        py_type = map_vetro_type_to_python(html_input, permitted)

        if py_type != "str":
            type_overrides[name] = py_type

    # Ensure vetro_id is always present
    if "vetro_id" not in columns:
        columns.insert(0, "vetro_id")

    return columns, type_overrides


@st.cache_data(ttl=3600)
def fetch_layer_schema(
    api_key: str, base_url: str = "https://api.vetro.io/v3"
) -> Dict[str, Any]:
    """Fetches layer definitions from API and returns a clean schema dict."""
    headers = {"Token": api_key}

    try:
        resp = requests.get(f"{base_url}/layers", headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        st.error("API Timeout: fetching layer schema took too long.")
        return {}
    except (requests.exceptions.RequestException, ValueError) as e:
        st.error(f"Failed to fetch layer schema: {e}")
        return {}

    schema = {}
    for layer in data.get("layers", []):
        layer_name = layer.get("label")
        if not layer_name or layer_name not in ALLOWED_LAYERS:
            continue

        attributes = layer.get("available_attributes", {})

        columns, type_overrides = _parse_layer_attributes(attributes)

        schema[layer_name] = {"columns": columns, "types": type_overrides}

    return schema
