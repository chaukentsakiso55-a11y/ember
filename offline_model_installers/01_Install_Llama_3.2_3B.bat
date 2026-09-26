@echo off
call "%~dp0_helpers\pull_model.bat" "llama3.2:3b" "Llama 3.2 3B" "about 2.0 GB" "Balanced general assistant; current Ember default family."
exit /b %errorlevel%
