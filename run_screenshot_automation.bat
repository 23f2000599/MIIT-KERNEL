@echo off
echo ========================================
echo Website Screenshot Automation Setup
echo ========================================

echo.
echo Installing Selenium dependencies...
pip install selenium==4.15.2 webdriver-manager==4.0.1 requests

echo.
echo Dependencies installed successfully!
echo.

echo Starting Flask application in background...
start /B python app.py

echo Waiting for Flask server to start...
timeout /t 10 /nobreak > nul

echo.
echo Running screenshot automation...
python comprehensive_screenshot_tool.py

echo.
echo Screenshot automation completed!
pause