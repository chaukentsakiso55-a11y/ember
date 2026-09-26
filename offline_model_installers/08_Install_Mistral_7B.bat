@echo off
call "%~dp0_helpers\pull_model.bat" "mistral:7b" "Mistral 7B" "about 4.4 GB" "General fallback model; already referenced by Ember as a fallback."
exit /b %errorlevel%
