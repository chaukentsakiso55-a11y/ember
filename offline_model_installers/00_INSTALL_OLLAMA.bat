@echo off
setlocal EnableExtensions
chcp 65001 >nul
cls
echo ================================================================
echo  EMBER - INSTALL OLLAMA FOR WINDOWS - FIXED
echo ================================================================
echo.
call "%~dp0_helpers\find_ollama.bat"
if not errorlevel 1 goto :already_installed

echo Ollama runs Ember's optional offline AI models on your PC.
echo This requires Windows 10 or later and an internet connection.
echo.
choice /C YN /N /M "Install Ollama now? [Y/N]: "
if errorlevel 2 exit /b 1

where winget >nul 2>&1
if errorlevel 1 goto :official_script
echo.
echo [1/2] Trying the Ollama.Ollama package via Windows winget...
winget install --exact --id Ollama.Ollama --source winget --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto :official_script
goto :verify

:official_script
echo.
echo [2/2] winget was unavailable or failed.
echo Official Ollama PowerShell installer: https://ollama.com/install.ps1
echo The fallback avoids the old BAT quoting bug.
choice /C YN /N /M "Run the official Ollama installation script? [Y/N]: "
if errorlevel 2 goto :manual_install
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; Invoke-Expression (Invoke-RestMethod -Uri 'https://ollama.com/install.ps1')"
if errorlevel 1 goto :manual_install

:verify
call "%~dp0_helpers\find_ollama.bat"
if errorlevel 1 (
  echo.
  echo [INFO] Installer completed but this window cannot find Ollama yet.
  echo Close and reopen the command window, or restart your PC.
  echo Then run 09_CHECK_INSTALLED_MODELS.bat to confirm installation.
  pause
  exit /b 3
)
echo.
echo [OK] Ollama installation detected:
"%OLLAMA_BIN%" --version
echo.
echo You can now download a model using one of the model BAT files.
pause
exit /b 0

:already_installed
echo [OK] Ollama is already installed:
"%OLLAMA_BIN%" --version
echo.
pause
exit /b 0

:manual_install
echo.
echo [ERROR] Ollama could not be installed automatically.
echo Download the Windows installer from its official site:
echo https://ollama.com/download/windows
echo Reopen this folder after installation and run a model BAT.
pause
exit /b 2
