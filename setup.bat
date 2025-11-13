@echo off
echo ==========================================
echo   Facebook Group Scraper - Setup
echo ==========================================
echo.

REM Check Python
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To use the tool:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run tool: python facebook_group_scraper.py
echo.
pause
