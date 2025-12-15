"""
Editor page
"""

import os
from typing import Optional, Tuple
import streamlit as st
import pandas as pd
from decouple import config

from vetro.api import VetroAPIClient

st.set_page_config(page_title="Vetro Editor", page_icon="🔧", layout="wide")

# Feature Type Column Configurations
FEATURE_COLUMNS = {
    "Flower Pot Dead End": [
        "ID",
        "Location",
        "Name",
        "Notes",
        "Size",
        "Type",
        "RUS Code",
        "vetro_id",
    ],
    "Service Location": [
        "ID",
        "Name",
        "Address",
        "Street Address",
        "City",
        "State",
        "Zip Code",
        "Location Type",
        "Note",
        "Drop Type",
        "Build",
        "Latitude",
        "Source",
        "County",
        "vetro_id",
    ],
    "Handhole": [
        "ID",
        "Name",
        "Location",
        "Type",
        "Note",
        "Build",
        "Owner",
        "RUS Code",
        "Size",
        "MST",
        "Splicing",
        "vetro_id",
    ],
    "Aerial Splice Closure": [
        "ID",
        "Name",
        "Owner",
        "Location",
        "Links",
        "Structure ID",
        "Note",
        "Build",
        "RUS Code",
        "HO 1",
        "vetro_id",
    ],
}

FEATURE_TYPE_KEYWORDS = {
    "flower": "Flower Pot Dead End",
    "pot": "Flower Pot Dead End",
    "service": "Service Location",
    "handhole": "Handhole",
    "splice": "Aerial Splice Closure",
    "closure": "Aerial Splice Closure",
}


def init_session_state():
    """Initialize commonly shared session state keys."""
    ss = st.session_state
    ss.setdefault("dataframes", {})
    ss.setdefault("feature_types", {})
    ss.setdefault("current_file", None)
    ss.setdefault("user_api_key", "")
    ss.setdefault("key_preference", "Use user key (if set)")
    ss.setdefault("editor_id", 0)


init_session_state()


def detect_feature_type(filename: str) -> Optional[str]:
    """Detect feature type from filename using keyword matching."""
    filename_lower = filename.lower()
    for k, v in FEATURE_TYPE_KEYWORDS.items():
        if k in filename_lower:
            return v
    return None


def get_effective_api_key() -> Optional[str]:
    """Determine which API key to use based on preferences."""
    backend_key = os.environ.get("VETRO_API_KEY", "") or config(
        "VETRO_API_KEY", default=""
    )
    pref = st.session_state.get("key_preference", "Use user key (if set)")
    user_key = st.session_state.get("user_api_key", "")

    if pref == "Always use backend key (if available)":
        return backend_key or (user_key or None)
    return user_key or backend_key or None


def compute_diff(
    original: pd.DataFrame, edited: pd.DataFrame, id_col: str = "vetro_id"
) -> pd.DataFrame:
    """Compute differences between original and edited DataFrames."""
    diffs = []

    # 1. Strategy: Compare by ID
    if id_col in original.columns and id_col in edited.columns:
        orig = original.set_index(id_col)
        new = edited.set_index(id_col)
        common = orig.index.intersection(new.index)

        for vid in common:
            for col in orig.columns:
                if col not in new.columns:
                    continue
                old = orig.at[vid, col]
                newv = new.at[vid, col]
                if pd.isna(old) and pd.isna(newv):
                    continue
                if old == newv:
                    continue
                diffs.append(
                    {
                        "vetro_id": vid,
                        "column": col,
                        "old_value": old,
                        "new_value": newv,
                    }
                )

    # 2. Strategy: Compare by Index (Fallback)
    else:
        for i in range(min(len(original), len(edited))):
            for col in original.columns:
                if col not in edited.columns:
                    continue
                old = original.iloc[i][col]
                newv = edited.iloc[i][col]
                if pd.isna(old) and pd.isna(newv):
                    continue
                if old == newv:
                    continue
                diffs.append(
                    {"row_index": i, "column": col, "old_value": old, "new_value": newv}
                )

    return pd.DataFrame(diffs)


def get_changed_rows(
    diff_df: pd.DataFrame, edited_df: pd.DataFrame, id_col: str = "vetro_id"
) -> pd.DataFrame:
    """Filter the edited DataFrame to return only rows that changed."""
    if diff_df.empty:
        return pd.DataFrame()

    if id_col in diff_df.columns:
        changed_ids = set(diff_df[id_col].unique())
        return edited_df[edited_df[id_col].isin(changed_ids)].copy()

    changed_indices = set(diff_df["row_index"].unique())
    return edited_df.iloc[list(changed_indices)].copy()


def handle_file_upload():
    """Render sidebar uploader and load data into session state."""
    with st.sidebar:
        st.markdown("### 📁 Upload CSV Files")
        uploaded_files = st.file_uploader(
            "Choose CSV files", type=["csv"], accept_multiple_files=True
        )

        if uploaded_files:
            for f in uploaded_files:
                if f.name not in st.session_state["dataframes"]:
                    try:
                        df = pd.read_csv(f)
                        st.session_state["dataframes"][f.name] = df
                        st.session_state["feature_types"][f.name] = detect_feature_type(
                            f.name
                        )
                        st.success(f"✅ Loaded {f.name} ({len(df)} rows)")
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        st.error(f"❌ Failed to load {f.name}: {e}")

        if st.session_state["dataframes"]:
            file_list = list(st.session_state["dataframes"].keys())
            current = st.selectbox(
                "Active file", options=file_list, key="file_selector"
            )

            # Reset editor state if file changes
            if current != st.session_state.get("current_file"):
                st.session_state["current_file"] = current
                st.session_state["editor_id"] += 1

        st.divider()
        # Return batch size as it's needed for the API
        return st.slider("Batch size", min_value=1, max_value=50, value=10)
    return 10


def render_data_editor(current_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Render the main data editor widget and return (edited_df, diff_df)."""
    original_df = st.session_state["dataframes"][current_file]
    feature_type = st.session_state["feature_types"].get(current_file)

    st.markdown(f"## Editing: **{current_file}**")
    if feature_type:
        st.info(f"🎯 Detected feature type: {feature_type}")

    # Determine columns
    if feature_type and feature_type in FEATURE_COLUMNS:
        display_cols = [
            c for c in FEATURE_COLUMNS[feature_type] if c in original_df.columns
        ]
    else:
        display_cols = original_df.columns.tolist()

    st.markdown("### 📝 Edit Data")
    st.caption("💡 Drag handle to fill. Copy/Paste supported.")

    column_config = {"vetro_id": st.column_config.TextColumn("Vetro ID", disabled=True)}

    # Use dictionary syntax for Pylint safety
    editor_key = f"editor_{current_file}_{st.session_state['editor_id']}"

    edited_df = st.data_editor(
        original_df[display_cols],
        key=editor_key,
        height=500,
        use_container_width=True,
        num_rows="dynamic",
        column_config=column_config,
    )

    # Compute diff
    diff_df = compute_diff(original_df, edited_df)

    st.markdown("### 🔎 Review Changes")
    if len(diff_df) > 0:
        st.markdown(f"**Detected changes:** {len(diff_df)} cells modified")
        st.dataframe(diff_df.head(100), height=300)
    else:
        st.info("✅ No changes detected.")

    return edited_df, diff_df


def handle_api_submission(
    current_file: str, edited_df: pd.DataFrame, diff_df: pd.DataFrame, batch_size: int
):
    """Handle the API update logic."""
    st.markdown("### 🚀 Send Updates")
    effective_key = get_effective_api_key()

    if not effective_key:
        return

    changed_rows = get_changed_rows(diff_df, edited_df)
    if changed_rows.empty:
        return

    st.info(f"Ready to update {len(changed_rows)} features.")

    col_dry, col_conf = st.columns([1, 2])
    with col_dry:
        dry_run = st.checkbox("🧪 Dry run", value=False)
    with col_conf:
        confirm = st.checkbox("✅ I have reviewed the changes", value=False)

    if st.button("🚀 Confirm and Update"):
        if not confirm:
            st.warning("⚠️ Please check the confirmation box.")
            return

        client = VetroAPIClient(effective_key)

        if dry_run:
            preview = client.convert_df_to_features(changed_rows.head(5))
            st.json({"features": preview, "note": "Preview of first 5 items"})
        else:
            st.info("📡 Sending updates...")
            prog_bar = st.progress(0)

            def cb(p):
                prog_bar.progress(p)

            results = client.batch_update_features(
                changed_rows, batch_size=batch_size, progress_callback=cb
            )

            if results.get("failed", 0) == 0 and not results.get("rate_limited"):
                st.success(f"✅ Updated {results['successful']} features!")
                # Update master dataframe
                st.session_state["dataframes"][current_file].update(edited_df)
                st.session_state["editor_id"] += 1
                st.rerun()
            else:
                st.warning(
                    f"⚠️ Partial success: {results['successful']} ok, {results['failed']} failed."
                )
                if results.get("errors"):
                    with st.expander("View Errors"):
                        st.write(results["errors"])


def main():
    """Main execution function for the editor page."""
    st.markdown("# 🔧 :blue[Vetro Feature Layer Editor]")

    # 1. Sidebar & File Loading
    batch_size = handle_file_upload()

    # 2. Main Logic
    if not st.session_state.get("dataframes") or not st.session_state.get(
        "current_file"
    ):
        st.info("👈 Please upload and select a file to begin.")
        return

    current = st.session_state["current_file"]

    # 3. Editor Interface
    edited_df, diff_df = render_data_editor(current)

    # 4. Action Buttons (Save/Discard/Download)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("💾 Save Snapshot"):
            st.session_state["dataframes"][current].update(edited_df)
            st.session_state["editor_id"] += 1
            st.success("Saved!")
            st.rerun()
    with col2:
        if st.button("↩️ Discard all edits"):
            st.session_state["editor_id"] += 1
            st.rerun()
    with col3:
        if st.button("⬇️ Download diff"):
            st.download_button(
                "Download diff", diff_df.to_csv(index=False), f"{current}_diff.csv"
            )

    st.divider()

    # 5. API Logic
    handle_api_submission(current, edited_df, diff_df, batch_size)

    # 6. Export
    st.markdown("### 💾 Export")
    if st.button("📥 Download CSV"):
        st.download_button(
            "Click to Download", edited_df.to_csv(index=False), f"{current}_edited.csv"
        )


if __name__ == "__main__":
    main()
