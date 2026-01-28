# Vetro Feature Layer Editor

A Streamlit-based GUI application for editing and updating Vetro feature layer properties via CSV files.

## 🌟 Features

- 📁 **Multi-file CSV management** - Upload and edit multiple CSV files simultaneously
- ✏️ **Interactive editing** - Edit cells, add/delete rows with data validation
- 🧠 **Persistent Session State** - API keys and preferences are saved securely and survive page refreshes
- 🎯 **Dynamic Schema Detection** - Automatically fetches layer definitions (columns/types) from the Vetro API
- 🔍 **Advanced filtering** - Search and filter data by any column
- 🚀 **Smart API Integration**
    - **Throttling:** Automatically pauses between batches to respect rate limits (1 req/sec).
    - **Robust Retries:** Automatically switches to row-by-row updates if a batch fails (isolating "poison" data).
    - **Type Enforcement:** Automatically converts columns like `Height` (int) and `Permitted` (bool) to the correct JSON types based on API metadata.
- 🔄 **Update Strategies** - Choose between "Smart Sync" (changes only) or "Force Push" (bulk update all rows).
- 💾 **Export options** - Download edited files as CSV or JSON
- 🎯 **Dry run mode** - Preview API payloads before sending
- 📊 **Progress tracking** - Monitor batch update progress in real-time
- 🔒 **Backend API key support** - Configure once via environment variable

## 📋 Supported Feature Types

The application currently supports the following feature layers. Auto-detection is based on filename keywords or column structure.

| Feature Type | Detection Keywords (Filename) |
|-------------|-------------------------------|
| **Flower Pot Dead End** | flower, pot |
| **Service Location** | service |
| **Handhole** | handhole |
| **Aerial Splice Closure** | splice, closure |
| **Pole** | pole |
| **Pigtail** | pigtail |
| **Lateral** | lateral |
| **Backbone** | backbone |
| **Duct** | duct |
| **Drop** | drop |
| **Cabinet (FDH)** | cabinet, fdh |
| **CO** | co |
| **NAP** | nap |
| **Slack Loop** | slack, loop |

*Note: Supported layers are configured in `vetro/constants.py`.*

## 🚀 Installation

### Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR **Python 3.9-3.11** for local installation

### Option 1: Docker (Recommended)

1. **Clone or download the project files:**
   ```bash
   mkdir vetro_editor
   cd vetro_editor

```

2. **Ensure your project structure is correct (see Project Structure below).**
3. **Build and run:**

```bash
docker-compose build
docker-compose up -d

```

4. **Access the app:**

* Open your browser: http://localhost:8501

### Option 2: Local Python Installation

1. **Create virtual environment:**

```bash
python -m venv venv

```

2. **Activate virtual environment:**

* **Windows:** `venv\Scripts\activate`
* **Mac/Linux:** `source venv/bin/activate`

3. **Install dependencies:**

```bash
pip install -r requirements.txt

```

4. **Run the application:**

```bash
streamlit run main.py

```

## 📖 Usage Guide

### 1. Configuration

#### API Key Setup (Choose one method)

**Option A: Backend Configuration (Recommended)**

```bash
# Docker: Add to docker-compose.yml
environment:
  - VETRO_API_KEY=your_api_key_here

# Local: Set environment variable (system level)
export VETRO_API_KEY=your_api_key_here  # Mac/Linux
set VETRO_API_KEY=your_api_key_here     # Windows

# Local: Set environment variable (dev level)
# Create a .env file and add VETRO_API_KEY=your_api_key_here

```

**Option B: Enter in UI**

* Go to the **Settings** page via the sidebar.
* Enter your API Key.
* Choose your **Priority Logic** (whether to prefer the Backend key or your Session key).

### 2. Upload CSV Files

1. Go to the **Editor** page.
2. Click **"Browse files"** in the sidebar.
3. Select one or more CSV files.
4. Files are automatically loaded and feature type is detected.

**Note: ** Only CSV in UTF-8 format are supported at this time.

**CSV Requirements:**

* Must contain a `vetro_id` column (UUID format)
* Column names should match Vetro property names
* Columns starting with `v_` are excluded from API updates

### 3. Edit Data

**Edit Data Tab:**

* Click cells to edit values inline
* Add new rows with the "+" button
* Delete rows by selecting and pressing delete
* Toggle `vetro_id` visibility with checkbox

**Filter & Search Tab:**

* Search within specific columns
* Filter by unique values
* View filtered results

### 4. Update Features via API

**API Update Tab:**

1. **Select Strategy:**

* **Force Push (Default):** Updates ALL rows in the table. Recommended for bulk edits.
* **Smart Sync:** Only updates rows that have changed in the editor.

2. **Dry Run (Recommended first):**

* Keep "Dry Run" checkbox enabled.
* Click "🚀 Confirm and Update".
* Review JSON payload preview.

3. **Actual Update:**

* Uncheck "Dry Run".
* Click "🚀 Confirm and Update".
* Monitor progress bar.

**What Gets Updated:**

* ✅ All properties (columns) except `vetro_id` and `v_*` columns
* ✅ **Type Conversion:** Fields like `Height` are automatically sent as Integers; `Permitted` as Booleans.
* ❌ Geometry is NOT modified
* ❌ x-vetro fields (layer_id, plan_id, etc.) are NOT modified

### 5. Export Data

**Export Tab:**

* Click "📥 Download CSV" to save your current work.

## ⚙️ Configuration Options

### API Settings (Sidebar)

| Setting | Default | Description |
| --- | --- | --- |
| **Batch Size** | 10 | Number of features per API call |
| **Priority Logic** | Use User Key | Decide which key takes precedence if both Backend and User keys exist |

### Rate Limits & Throttling

The application automatically handles Vetro API limits:

* **Throttling:** Adds a ~1.5s delay between batches to stay under the limit.
* **Retry Logic:** Retries failed requests up to 5 times with exponential backoff.

| Token Type | Rate Limit |
| --- | --- |
| **Personal** | 10 requests / 10 seconds |
| **Integration** | 200 requests / 10 seconds |

## 📁 Project Structure

```text
vetro_editor/
├── main.py                     # Application Entry Point (Home Page)
├── pages/                      # Streamlit Pages
│   ├── __init__.py
│   ├── editor.py               # Main Editor Logic
│   └── settings.py             # Configuration & Key Management
├── vetro/                      # Application Package
│   ├── __init__.py
│   ├── api.py                  # Vetro API Client
│   ├── config.py               # Configuration Utilities
│   ├── constants.py            # Layer Config & System Fields
│   ├── local_storage.py        # Browser Storage Helpers
│   ├── state.py                # Session State Management
│   ├── ui.py                   # Shared UI Components
│   └── version.py              # Version Definition
├── data/                       # (Optional) CSV files directory
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Docker services configuration
├── .dockerignore               # Files to exclude from Docker build
├── requirements.txt            # Python dependencies
├── CHANGELOG.md                # Change history
└── README.md                   # This file

```

## 🔧 Troubleshooting

### Port Already in Use

**Problem:** Port 8501 is already in use

**Solution:** Change port in `docker-compose.yml`:

```yaml
ports:
  - "8502:8501"  # Changed from 8501:8501

```

Access at: http://localhost:8502

### Key Not Saving

**Problem:** API Key disappears after refreshing the page.

**Solution:** This is likely a caching issue. The application uses a robust state management system (`vetro/state.py`). Ensure you are running the latest version of the code and that your browser allows LocalStorage.

### Rate Limit Errors / 500 Errors

**Problem:** Updates are failing with 429 or 500 errors.

**Solutions:**

* Check the logs for error messages.
* Ensure your CSV data types match expectation (e.g., `Height` should be a number).

### Payload Too Large

**Problem:** The update fails (often with a 413 error) because the JSON payload exceeds the API's maximum size limit. This usually happens when rows contain very large text fields or when the batch size is too high.

**Solution:** Reduce the **Batch Size** in the sidebar (e.g., lower it from 100 to 50) and try again.

## 📝 API Reference

### Vetro API Endpoint

```
PATCH [https://api.vetro.io/v3/features](https://api.vetro.io/v3/features)

```

### Response Codes

| Code | Meaning |
| --- | --- |
| 200 | Success - Features updated |
| 400 | Bad Request - Invalid payload |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Feature doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Server Error - Often caused by bad data types |
