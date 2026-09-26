@echo off
setlocal EnableExtensions
chcp 65001 >nul
cls
echo ================================================================
echo  EMBER - OFFLINE MODEL STATUS
echo ================================================================
echo.
call "%~dp0_helpers\find_ollama.bat"
if errorlevel 1 (
  echo [ERROR] Ollama is not installed or cannot be found.
  echo Run 00_INSTALL_OLLAMA.bat, then reopen this window.
  pause
  exit /b 1
)
"%OLLAMA_BIN%" --version
echo.
"%OLLAMA_BIN%" list
echo.
pause
