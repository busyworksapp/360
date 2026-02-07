@echo off
echo ================================================
echo SSL/HTTPS Cache Cleanup Script
echo ================================================
echo.
echo This script will:
echo 1. Clear DNS cache
echo 2. Reset Winsock
echo 3. Clear Chrome SSL cache
echo 4. Clear Edge SSL cache
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/4] Clearing DNS Cache...
ipconfig /flushdns
echo Done!

echo.
echo [2/4] Resetting Winsock...
netsh winsock reset
echo Done!

echo.
echo [3/4] Clearing Chrome SSL Cache...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\TransportSecurity" (
    del "%LOCALAPPDATA%\Google\Chrome\User Data\Default\TransportSecurity" /F /Q
    echo Chrome SSL cache cleared!
) else (
    echo Chrome SSL cache not found (Chrome might not be installed)
)

if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network Persistent State" (
    del "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network Persistent State" /F /Q
    echo Chrome network state cleared!
) else (
    echo Chrome network state not found
)

echo.
echo [4/4] Clearing Edge SSL Cache...
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\TransportSecurity" (
    del "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\TransportSecurity" /F /Q
    echo Edge SSL cache cleared!
) else (
    echo Edge SSL cache not found (Edge might not be installed)
)

if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Network Persistent State" (
    del "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Network Persistent State" /F /Q
    echo Edge network state cleared!
) else (
    echo Edge network state not found
)

echo.
echo ================================================
echo Cleanup Complete!
echo ================================================
echo.
echo IMPORTANT: 
echo 1. Close ALL browser windows
echo 2. Restart your browser
echo 3. Visit: https://www.360degreesupply.co.za/
echo.
echo You should now see the secure padlock icon!
echo.
echo Press any key to exit...
pause >nul
