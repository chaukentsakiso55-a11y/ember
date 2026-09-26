@echo off
call "%~dp0_helpers\pull_model.bat" "qwen2.5:3b" "Qwen 2.5 3B" "about 1.9 GB" "Light general model with multilingual and structured-output strengths."
exit /b %errorlevel%
