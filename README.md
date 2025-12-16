# Vetro Feature Layer CSV Editor

A Streamlit-based GUI application for editing and updating Vetro feature layer properties via CSV files.

## 🌟 Features
- **Interactive Editor:** Excel-like editing with drag-fill support.
- **Secure Configuration:** Browser-based local storage for API keys.
- **Modern UI:** Clean sidebar navigation with status indicators.
- **Vetro API Integration:** Robust client with exponential backoff and retry logic.

## 🧭 Navigation
- **Home:** Welcome screen and security best practices.
- **Editor:** (Coming Soon)
- **Settings:** User preferences.

## 📝 API Reference
The application communicates with `PATCH https://api.vetro.io/v3/features`.

## ⚙️ Configuration
1. Go to **Settings**.
2. Enter your Vetro API Key.
3. Click **Save Key** to store it in your browser.

## 📖 Usage Guide
1. Upload a CSV file in the **Editor** tab.
2. Edit cells directly in the grid.
3. Review changes in the "Review" section.
4. Click **Update** to send changes to Vetro.

## 📋 Supported Feature Types
- Flower Pot Dead End
- Service Location
- Handhole
- Aerial Splice Closure
- Pole