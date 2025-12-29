"""
Vetro API client encapsulating PATCH calls, retries/backoff, and helpers to convert
Pandas DataFrames to Vetro feature payloads.
"""

import time
import logging
from typing import List, Dict
import requests
import pandas as pd

# Configure logger
logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


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
        request_timeout: int = 30,
        max_retries: int = 5,
        initial_backoff: float = 2.0, 
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
                progress_callback(min((start + batch_size) / n, 1.0))

        return results

    def convert_df_to_features(self, df: pd.DataFrame) -> List[Dict]:
        """
        Convert DataFrame rows to the Vetro 'Feature' JSON payload.
        Only includes properties (no geometry).
        Skips columns named 'vetro_id' and any column starting with 'v_'.
        
        Updated logic: Preserves explicit None values (sending them as null).
        """
        features = []
        for _, row in df.iterrows():
            properties = {}
            for col in df.columns:
                if col == "vetro_id" or str(col).startswith("v_"):
                    continue             
                val = row[col]
                
                # Check for explicit None (passed from Force Push logic)
                if val is None:
                    properties[col] = None
                
                # Check for existing data (Strings, numbers, etc.)
                elif pd.notna(val):
                    properties[col] = str(val)
            vetro_id = row.get("vetro_id")
            feature = {
                "type": "Feature",
                "x-vetro": {"vetro_id": vetro_id},
                "properties": properties,
            }
            features.append(feature)
        return features
