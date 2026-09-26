@echo off
call "%~dp0_helpers\pull_model.bat" "qwen2.5-coder:3b" "Qwen 2.5 Coder 3B" "about 1.9 GB" "Light coding model for code generation, reasoning, and fixing."
exit /b %errorlevel%
