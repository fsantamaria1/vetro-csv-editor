# Changelog

## 1.2.0 — 2025-12-23
### Added
- Robust shared session-state system with navigation-safe persistence (`vetro/state.py`)
- Auto-loading and bi-directional syncing of API keys and preferences from browser LocalStorage
- Centralized state initialization via `init_shared_state`
- Safety vaults (`_api_key_store`, `_pref_store`) to preserve values across Streamlit page reloads

### Changed
- Editor page updated to use centralized shared state instead of local initialization
- Settings page refactored to decouple widget keys from data variables, preventing state loss
- Improved state synchronization callbacks for user API key and preference updates

### Fixed
- Resolved Pylint protected-access warnings by replacing attribute access with dictionary access in session state
- Ensured consistent state persistence when navigating between Editor and Settings pages

---

## 1.1.0 — 2025-12-22
### Added
- Centralized backend API key loading (`vetro/config.py`)
- Added version management (`vetro/version.py`)
- Improved settings page and key‑handling logic
- Added browser storage persistence for user keys
- Added UI shell and sidebar component
- Added API client with retry logic
- Added security best‑practices section
- Added captions and status indicators

### Changed
- Refactored multiple modules to use shared configuration helpers
- Improved consistency across pages (settings, main, sidebar)

---

## 1.0.0 — 2025-12-10
### Added
- Initial project structure
- Basic UI layout
- Initial settings page
- Initial README
- Project initialization and first working version

## v1.8.1 (2026-01-05)

### Fix

- **ci**: force changelog addition in release workflow

## v1.8.0 (2026-01-05)

### Feat

- **editor**: enforce strict pole data types for api compliance
- **editor**: add force push mode with null value support
- **api**: support explicit null values in feature conversion
- **editor**: Add an option for a force push all rows in the editor
- **config**: add helper to resolve active api key based on user preference

### Fix

- **editor**: enforce integer type for Entry Order field
- **api**: support native int and bool types in json payload
- **api**: add client-side throttling and increase retries
- **main**: add session state initialization to prevent data loss on refresh
- **ui**: simplify status label logic based on strict preferences
- **config**: enforce strict api key preference logic
- **ui**: ensure connection status reflects active key preference

### Refactor

- **editor**: Removed and remaned columns in the 'Pole' feature list
- **editor**: use centralized api key resolution logic

## v1.2.0 (2025-12-23)

### Feat

- **state**: implement robust shared session state with navigation safety

### Fix

- **settings**: decouple settings widgets from data variables to persist state

### Refactor

- **editor**: integrate editor page with centralized shared state

## v1.1.0 (2025-12-23)
