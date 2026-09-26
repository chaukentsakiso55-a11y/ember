@echo off
call "%~dp0_helpers\pull_model.bat" "qwen2.5:7b" "Qwen 2.5 7B" "about 4.7 GB" "Stronger general model; already referenced by Ember as a fallback."
exit /b %errorlevel%
