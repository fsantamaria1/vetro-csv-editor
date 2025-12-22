@echo off
echo ==========================================
echo   Vetro CSV Editor - Setup Script
echo ==========================================
echo.

REM Check Python version
python --version
echo.

REM Create virtual environment
echo [*] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [X] Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip to ensure it can find the latest wheels
echo [*] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo.
echo [*] Installing latest compatible libraries...
echo     (This may take a moment)
echo.

REM We use --prefer-binary to avoid compilation if possible
pip install --prefer-binary -r requirements.txt

if errorlevel 1 (
    echo.
    echo [X] Installation failed.
    echo.
    echo CRITICAL NOTE: 
    echo Since Python 3.14 is very new (released Oct 2025), some libraries 
    echo may not have published compatible binaries yet.
    echo.
    echo IF THIS KEEPS FAILING:
    echo Please install Python 3.12 or 3.13 alongside 3.14 and use that 
    echo for this specific tool.
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   [OK] Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo   1. venv\Scripts\activate
echo   2. streamlit run vetro_editor_app.py
echo.
pause