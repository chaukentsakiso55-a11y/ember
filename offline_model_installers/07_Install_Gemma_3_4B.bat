@echo off
call "%~dp0_helpers\pull_model.bat" "gemma3:4b" "Gemma 3 4B" "about 3.3 GB" "Compact multimodal text/image model; useful for local vision-capable workflows."
exit /b %errorlevel%
