"""
Editor page
"""

from typing import Optional, Tuple, List
import streamlit as st
import pandas as pd
from pandas.errors import ParserError

from vetro.api import VetroAPIClient, fetch_layer_schema
from vetro.config import get_effective_api_key
from vetro.state import init_shared_state, sync_storage

st.set_page_config(page_title="Vetro Editor", page_icon="🔧", layout="wide")

FEATURE_TYPE_KEYWORDS = {
    "flower": "Flower Pot Dead End",
    "pot": "Flower Pot Dead End",
    "service": "Service Location",
    "handhole": "Handhole",
    "splice": "Aerial Splice Closure",
    "closure": "Aerial Splice Closure",
    "pole": "Pole",
}


def init_session_state():
    """Initialize session state."""
    # 1. Initialize shared state (API keys, preferences, vaults)
    init_shared_state()

    # 2. Initialize editor-specific state
    ss = st.session_state
    ss.setdefault("dataframes", {})
    ss.setdefault("feature_types", {})
    ss.setdefault("current_file", None)
    ss.setdefault("editor_id", 0)
    ss.setdefault("layer_schema", {})


init_session_state()


def ensure_schema_loaded():
    """Load schema into session state if it's missing."""
    if not st.session_state["layer_schema"]:
        api_key = get_effective_api_key()
        if api_key:
            with st.spinner("Fetching Layer Schema..."):
                st.session_state["layer_schema"] = fetch_layer_schema(api_key)


ensure_schema_loaded()


def detect_feature_type(filename: str, columns: List[str] = None) -> Optional[str]:
    """Detect feature type using cascading strategy with Dynamic Schema."""
    schema = st.session_state["layer_schema"]

    # 1. Filename Strategy
    filename_lower = filename.lower()
    for k, v in FEATURE_TYPE_KEYWORDS.items():
        if k in filename_lower:
            if v in schema:
                return v

    # 2. Dynamic Column Strategy
    if columns and schema:
        df_cols_set = set(columns)

        # Strict Match
        for f_type, config in schema.items():
            known_cols = config["columns"]
            detection_cols = {c for c in known_cols if c != "vetro_id"}
            if detection_cols.issubset(df_cols_set):
                return f_type

        # Heuristic Match
        best_match = None
        max_score = 0

        for f_type, config in schema.items():
            known_cols = set(config["columns"])
            overlap = len(df_cols_set.intersection(known_cols))

            if overlap > max_score and overlap >= 3:
                max_score = overlap
                best_match = f_type

        if best_match:
            return best_match

    return None


def enforce_column_types(df: pd.DataFrame, feature_type: str) -> pd.DataFrame:
    """Convert specific columns to their required API types."""
    schema = st.session_state["layer_schema"]

    if not feature_type or feature_type not in schema:
        return df

    type_map = schema[feature_type].get("types", {})
    df_clean = df.copy()

    for col, dtype in type_map.items():
        if col not in df_clean.columns:
            continue

        if dtype == "int":
            numeric_series = pd.to_numeric(df_clean[col], errors="coerce")
            df_clean[col] = numeric_series.apply(
                lambda x: int(x) if pd.notna(x) else None
            )
        elif dtype == "float":
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        elif dtype == "bool":

            def parse_bool(x):
                if pd.isna(x) or x == "":
                    return None
                s = str(x).lower().strip()
                if s in ["true", "1", "yes", "y", "t"]:
                    return True
                if s in ["false", "0", "no", "n", "f"]:
                    return False
                return None

            df_clean[col] = df_clean[col].apply(parse_bool)

    return df_clean


def compute_diff(
    original: pd.DataFrame, edited: pd.DataFrame, id_col: str = "vetro_id"
) -> pd.DataFrame:
    """Compute differences between original and edited DataFrames."""

    # 1. Align DataFrames based on available columns
    # If ID exists, map by ID. Otherwise, map by row index.
    if id_col in original.columns and id_col in edited.columns:
        orig = original.set_index(id_col)
        new = edited.set_index(id_col)
        key_label = "vetro_id"
    else:
        orig = original
        new = edited
        key_label = "row_index"

    # 2. Determine common scope (Rows and Columns)
    # This replaces the manual 'min(len)' and column checks
    common_index = orig.index.intersection(new.index)
    common_cols = orig.columns.intersection(new.columns)

    diffs = []

    # 3. Unified Comparison Loop
    for idx in common_index:
        for col in common_cols:
            old = orig.at[idx, col]
            newv = new.at[idx, col]

            # Safe NA Comparison Logic
            is_old_na = pd.isna(old)
            is_new_na = pd.isna(newv)

            # A. Both missing -> Equal
            if is_old_na and is_new_na:
                continue

            # B. One missing, one present -> Changed
            if is_old_na != is_new_na:
                pass

            # C. Both present -> Check Equality
            elif old == newv:
                continue

            diffs.append(
                {key_label: idx, "column": col, "old_value": old, "new_value": newv}
            )

    diff_df = pd.DataFrame(diffs)

    # 4. Type safety for Arrow/Streamlit
    if not diff_df.empty:
        diff_df["old_value"] = diff_df["old_value"].astype(str)
        diff_df["new_value"] = diff_df["new_value"].astype(str)

    return diff_df


def get_changed_rows(
    diff_df: pd.DataFrame, edited_df: pd.DataFrame, id_col: str = "vetro_id"
) -> pd.DataFrame:
    """Filter the edited DataFrame to return only rows/columns that changed."""
    if diff_df.empty:
        return pd.DataFrame()

    if id_col in diff_df.columns:
        # Pivot: Index=ID, Columns=Changed Fields, Values=New Value
        delta_df = diff_df.pivot(index=id_col, columns="column", values="new_value")

        # Reset index so 'vetro_id' becomes a regular column again
        delta_df.reset_index(inplace=True)
        return delta_df

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

                        detected_type = detect_feature_type(f.name, df.columns.tolist())
                        st.session_state["feature_types"][f.name] = detected_type

                        if detected_type:
                            st.success(f"✅ Loaded {f.name}")
                        else:
                            st.warning(f"⚠️ Loaded {f.name} (Type Unknown)")
                    except (ParserError, UnicodeDecodeError, ValueError) as e:
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
        return st.slider(
            "Batch Size (Features per Request)",
            min_value=1,
            max_value=100,
            value=50,
            help="""
            Determines how many rows are sent to the API in a single call.
            - **Default (50):** Good for most updates.
            - **Lower (10-20):** Use if you encounter '413 (Payload Too Large)' or '500' errors.
            """,
        )
    return 50


def _prepare_editor_data(
    df: pd.DataFrame, schema: dict, feature_type: Optional[str]
) -> Tuple[pd.DataFrame, dict]:
    """
    Helper to prepare dataframe types and column config for the editor.
    """
    df_edit = df.copy()
    col_config = {"vetro_id": st.column_config.TextColumn("Vetro ID", disabled=True)}

    if not feature_type or feature_type not in schema:
        # Default behavior for unknown types
        return df_edit, col_config

    layer_config = schema[feature_type]
    type_map = layer_config.get("types", {})

    for col in df_edit.columns:
        if col == "vetro_id":
            continue

        # 1. Strict Numeric/Bool Fields
        if col in type_map:
            dtype = type_map[col]
            if dtype == "int":
                col_config[col] = st.column_config.NumberColumn(col, step=1)
                df_edit[col] = pd.to_numeric(df_edit[col], errors="coerce").astype(
                    "Int64"
                )
            elif dtype == "float":
                col_config[col] = st.column_config.NumberColumn(col)
                df_edit[col] = pd.to_numeric(df_edit[col], errors="coerce")
            elif dtype == "bool":
                col_config[col] = st.column_config.CheckboxColumn(col)

        # 2. Force TextColumn for everything else
        else:
            col_config[col] = st.column_config.TextColumn(col)
            # Cleaning lambda
            df_edit[col] = df_edit[col].apply(
                lambda val: (
                    str(int(val))
                    if (isinstance(val, float) and val.is_integer())
                    else (str(val) if pd.notna(val) else None)
                )
            )

    return df_edit, col_config


def render_data_editor(current_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Render the main data editor widget and return (edited_df, diff_df)."""
    original_df = st.session_state["dataframes"][current_file]
    current_type = st.session_state["feature_types"].get(current_file)
    schema = st.session_state["layer_schema"]

    st.markdown(f"## Editing: **{current_file}**")

    # Feature Type Selection UI
    col_config, col_status = st.columns([1, 2])

    with col_config:
        options = list(schema.keys())
        try:
            idx = options.index(current_type) if current_type in options else None
        except ValueError:
            idx = None

        # If no type detected, user sees placeholder
        selected_type = st.selectbox(
            "Feature Type Configuration",
            options=options,
            index=idx,
            placeholder="Select feature type...",
            help="Select the Vetro feature type to enable column filtering and type enforcement.",
            label_visibility="collapsed",
        )

    # If user changed the type manually, update session state and rerun to apply
    if selected_type != current_type:
        st.session_state["feature_types"][current_file] = selected_type
        st.rerun()

    # Status UI
    with col_status:
        if selected_type:
            auto_match = detect_feature_type(current_file, original_df.columns.tolist())
            if selected_type == auto_match:
                st.info(f"🎯 Auto-detected: **{selected_type}**")
            else:
                st.success(f"✅ Manual Configuration: **{selected_type}**")
        else:
            if not schema:
                st.error("⚠️ **API Error.** Could not fetch schema. Check API Key.")
            else:
                st.warning("⚠️ **Unknown Type.** Please select a feature type to edit.")

    st.divider()

    # Column Filtering
    if selected_type and selected_type in schema:
        allowed_cols = schema[selected_type]["columns"]
        display_cols = [c for c in allowed_cols if c in original_df.columns]
    else:
        display_cols = original_df.columns.tolist()

    # Ensure vetro_id is always visible and is the first column
    if "vetro_id" in original_df.columns:
        # If it was already in the list, remove it first
        if "vetro_id" in display_cols:
            display_cols.remove("vetro_id")
        # Insert at the very beginning
        display_cols.insert(0, "vetro_id")

    st.markdown("### 📝 Edit Data")

    # Prepare Data
    df_to_edit, column_config = _prepare_editor_data(
        original_df[display_cols], schema, selected_type
    )

    editor_key = f"editor_{current_file}_{st.session_state['editor_id']}"

    edited_df = st.data_editor(
        df_to_edit,
        key=editor_key,
        height=500,
        width="stretch",
        num_rows="dynamic",
        column_config=column_config,
    )

    # Compare against df_to_edit to avoid false positive diffs (e.g. 123 vs "123")
    diff_df = compute_diff(df_to_edit, edited_df)

    st.markdown("### 🔎 Review Changes")
    if len(diff_df) > 0:
        st.markdown(f"**Detected changes:** {len(diff_df)} cells modified")
        st.dataframe(diff_df.head(100), height=300)
    else:
        st.info("✅ No changes detected.")

    return edited_df, diff_df


def _perform_batch_update(
    client: VetroAPIClient, data: pd.DataFrame, batch_size: int, placeholders: dict
):
    """Helper to run the batch update loop and update UI metrics."""

    def update_dashboard(percent_complete, stats):
        placeholders["prog_bar"].progress(percent_complete)
        placeholders["success"].metric("✅ Success", stats["successful"])
        placeholders["failed"].metric("❌ Failed", stats["failed"])
        placeholders["pct"].metric("⏳ Progress", f"{int(percent_complete * 100)}%")

        if stats["errors"]:
            with placeholders["error_log"].container():
                with st.expander("🚨 Error Log", expanded=True):
                    st.error(f"Errors detected so far: {len(stats['errors'])}")
                    st.dataframe(pd.DataFrame(stats["errors"]), width="stretch")

    return client.batch_update_features(
        data, batch_size=batch_size, progress_callback=update_dashboard
    )


def handle_api_submission(
    current_file: str, edited_df: pd.DataFrame, diff_df: pd.DataFrame, batch_size: int
):
    """Handle the API update logic."""
    st.markdown("### 🚀 Send Updates")
    effective_key = get_effective_api_key()

    if not effective_key:
        return

    # Allow users to choose between Smart Sync (Diff) or Force Push (Bulk)
    with st.expander("⚙️ Update Strategy", expanded=True):
        update_mode = st.radio(
            "Mode",
            ["Smart Sync (Changes Only)", "Force Push All Rows"],
            index=1,
            horizontal=True,
            help="Smart Sync only sends rows you modified here. Force Push sends the entire file.",
        )

    # Logic to select which rows to send
    if update_mode == "Smart Sync (Changes Only)":
        changed_rows = get_changed_rows(diff_df, edited_df)
        if changed_rows.empty:
            st.info("✅ No changes detected to sync.")
            return
    else:
        # Force Push: Send the entire DataFrame
        changed_rows = edited_df.copy()

        # Replace NaN with Python None
        # This ensures the JSON serializer sends 'null' instead of empty strings or errors.
        changed_rows = changed_rows.astype(object).where(pd.notnull(changed_rows), None)

        st.warning(
            f"""⚠️ **Force Push Mode**: You are about to update {len(changed_rows)} features.
            This will overwrite data in Vetro with the values in this table."""
        )

    # Enforce Column Data Types (Int/Bool)
    feature_type = st.session_state["feature_types"].get(current_file)
    if feature_type:
        changed_rows = enforce_column_types(changed_rows, feature_type)

    st.info(f"Ready to update {len(changed_rows)} features.")

    col_conf, col_dry = st.columns([1, 2])
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
            # Generate preview from the sparse dataframe
            preview = client.convert_df_to_features(changed_rows.head(5))
            st.json({"features": preview, "note": f"Preview ({update_mode})"})
            return

        # UI Setup for Progress
        st.divider()
        st.markdown("### 📡 Update Progress")
        prog_bar = st.progress(0)
        m1, m2, m3 = st.columns(3)

        # Helper dict to pass to the update function
        placeholders = {
            "prog_bar": prog_bar,
            "success": m1.empty(),
            "failed": m2.empty(),
            "pct": m3.empty(),
            "error_log": st.empty(),
        }

        # Init Metrics
        placeholders["success"].metric("✅ Success", 0)
        placeholders["failed"].metric("❌ Failed", 0)
        placeholders["pct"].metric("⏳ Progress", "0%")

        # Run Update
        results = _perform_batch_update(client, changed_rows, batch_size, placeholders)

        if results.get("failed", 0) == 0 and not results.get("rate_limited"):
            st.success(f"✅ Updated {results['successful']} features!")
            st.session_state["dataframes"][current_file].update(edited_df)
            st.session_state["editor_id"] += 1
        elif results["successful"] == 0:
            st.error(f"❌ Update Failed: 0 ok, {results['failed']} failed.")
        else:
            st.warning(
                f"⚠️ Partial success: {results['successful']} ok, {results['failed']} failed."
            )


def main():
    """Main execution function for the editor page."""
    # Sync storage (Auto-load keys if landing here directly)
    sync_storage()

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
