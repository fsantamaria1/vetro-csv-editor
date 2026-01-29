## v1.13.4 (2026-01-29)

### Fix

- **api**: Add EXCLUDED_FIELDS and SYSTEM_FIELDS to block specific business columns from and system columns from being edited

### Refactor

- **constants**: create the list of EXCLUDED_FIELDS

## v1.13.3 (2026-01-22)

### Refactor

- **architecture**: extract configuration constants to dedicated module
- **constants**: Extract configuration constants from editor.py and api.py

## v1.13.2 (2026-01-22)

### Fix

- **editor**: fix incompatibility warning when saving Float64 columns

## v1.13.1 (2026-01-22)

### Fix

- **editor**: handle pd.NA comparisons safely in compute_diff

### Refactor

- **editor**: unify compute_diff logic to eliminate code duplication

## v1.13.0 (2026-01-22)

### Feat

- **api**: add dynamic schema fetching and type mapping

### Refactor

- **editor**: extract helpers to reduce complexity and fix linting errors
- **editor**: replace static config with api-driven schema and string enforcement

## v1.12.0 (2026-01-16)

### Feat

- **editor**: Add "Apt / Unit" and "Serviceable Date" to Service Location columns

## v1.11.0 (2026-01-16)

### Feat

- **editor**: add manual feature type selection dropdown
- **editor**: implement column-based feature detection strategies

### Fix

- **editor**: improve feature selection layout and status feedback

## v1.10.1 (2026-01-12)

### Fix

- **editor**: Remove boolean type from the Build property of multiple feature layers (#35)

## v1.10.0 (2026-01-08)

### Feat

- add live progress dashboard and real-time error logging (#33)

## v1.9.0 (2026-01-05)

### Feat

- **editor**: add column data types for the remaining layers

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
