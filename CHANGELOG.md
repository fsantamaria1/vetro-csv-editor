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
