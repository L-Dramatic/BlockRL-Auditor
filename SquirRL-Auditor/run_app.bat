@echo off
echo ========================================
echo    SquirRL-Auditor Web Application
echo ========================================
echo.
echo Starting Streamlit server...
echo.

cd /d "%~dp0"
streamlit run app/main.py --server.port 8501

pause



