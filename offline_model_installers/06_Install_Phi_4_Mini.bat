@echo off
call "%~dp0_helpers\pull_model.bat" "phi4-mini" "Phi-4 Mini 3.8B" "about 2.5 GB" "Compact reasoning, math, multilingual, and tool-capable model."
exit /b %errorlevel%
