@echo off
set "OLLAMA_BIN="
where ollama.exe >nul 2>&1
if errorlevel 1 goto :usual_locations
for /f "delims=" %%I in ('where ollama.exe 2^>nul') do if not defined OLLAMA_BIN set "OLLAMA_BIN=%%I"
if defined OLLAMA_BIN exit /b 0

:usual_locations
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_BIN=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if defined OLLAMA_BIN exit /b 0
if exist "%ProgramFiles%\Ollama\ollama.exe" set "OLLAMA_BIN=%ProgramFiles%\Ollama\ollama.exe"
if defined OLLAMA_BIN exit /b 0
exit /b 1
