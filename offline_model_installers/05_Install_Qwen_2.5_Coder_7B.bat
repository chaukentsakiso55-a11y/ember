@echo off
call "%~dp0_helpers\pull_model.bat" "qwen2.5-coder:7b" "Qwen 2.5 Coder 7B" "about 4.7 GB" "Stronger coding model for development work."
exit /b %errorlevel%
