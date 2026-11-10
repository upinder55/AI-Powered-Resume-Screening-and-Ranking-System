@echo off
echo ===================================================
echo Starting AI Powered Resume Screening & Ranking System
echo ===================================================
cd /d "%~dp0"
echo Active Directory: %CD%
echo Starting Flask web server at http://127.0.0.1:5000...
python app.py
pause
