@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Install Python 3.11 or 3.12, then run this file again.
  pause
  exit /b 1
)
set PYTHON_CMD=
py -3.12 -c "import sys; print(sys.version)" >nul 2>nul
if not errorlevel 1 set PYTHON_CMD=py -3.12
if not defined PYTHON_CMD (
  py -3.11 -c "import sys; print(sys.version)" >nul 2>nul
  if not errorlevel 1 set PYTHON_CMD=py -3.11
)
if not defined PYTHON_CMD (
  echo Python 3.11 or 3.12 is required. Python 3.13+ may not support all dependencies.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe %PYTHON_CMD% -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
call CREATE_EMBER_ICON.bat
call RUN_EMBER.bat
exit /b 0
:failed
echo Installation failed. Review the error above.
pause
exit /b 1
