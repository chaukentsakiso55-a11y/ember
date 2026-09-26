@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "MODEL=%~1"
set "DISPLAY=%~2"
set "SIZE=%~3"
set "NOTE=%~4"
if "%MODEL%"=="" (
  echo [ERROR] Missing model argument.
  exit /b 2
)
cls
echo ================================================================
echo  EMBER OFFLINE MODEL INSTALLER
echo ================================================================
echo  Model : %DISPLAY%
echo  Tag   : %MODEL%
echo  Size  : %SIZE%
echo  Use   : %NOTE%
echo ================================================================
echo.
call "%~dp0find_ollama.bat"
if errorlevel 1 (
  echo [ERROR] Ollama is not installed or cannot be found.
  echo Run 00_INSTALL_OLLAMA.bat first, then retry.
  if /I not "%EMBER_BULK_INSTALL%"=="1" pause
  exit /b 10
)
"%OLLAMA_BIN%" list >nul 2>&1
if errorlevel 1 (
  echo [INFO] Ollama is installed but the local server is not responding.
  echo [INFO] Starting Ollama in the background...
  start "Ember Ollama Server" /min "%OLLAMA_BIN%" serve
  timeout /t 5 /nobreak >nul
)
echo [EMBER] Downloading %MODEL% ...
echo Ollama will show the progress for this model below.
echo.
"%OLLAMA_BIN%" pull "%MODEL%"
if errorlevel 1 (
  echo.
  echo [ERROR] The model download did not complete.
  echo Check the internet connection, disk space and Ollama service.
  echo You can rerun this BAT to reuse previously downloaded layers.
  if /I not "%EMBER_BULK_INSTALL%"=="1" pause
  exit /b 20
)
echo.
echo [OK] %DISPLAY% is now installed locally.
if /I "%EMBER_BULK_INSTALL%"=="1" goto :done
echo.
choice /C YN /N /M "Make %DISPLAY% Ember's default local model? [Y/N]: "
if errorlevel 2 goto :done
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0set_default_model.ps1" -Model "%MODEL%" -EmberRoot "%~dp0..\.."
if errorlevel 1 (
  echo [WARN] Model installed, but Ember's default was not changed.
) else (
  echo [OK] Ember now defaults to %MODEL% for local Ollama chat.
)
:done
echo.
echo Installed Ollama models:
"%OLLAMA_BIN%" list
echo.
if /I not "%EMBER_BULK_INSTALL%"=="1" pause
exit /b 0
