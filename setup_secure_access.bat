@echo off
echo ========================================
echo Secure Network Access Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/3] Opening firewall port 5000...
netsh advfirewall firewall delete rule name="Flask App Port 5000" >nul 2>&1
netsh advfirewall firewall add rule name="Flask App Port 5000" dir=in action=allow protocol=TCP localport=5000
echo Done!
echo.

echo [2/3] Your local IP addresses:
ipconfig | findstr /i "IPv4"
echo.

echo [3/3] Starting secure server...
echo.
echo IMPORTANT: 
echo - Access locally: http://localhost:5000
echo - Access from network: http://YOUR_IP:5000
echo - For HTTPS, you need a domain and SSL certificate
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python app.py

pause
