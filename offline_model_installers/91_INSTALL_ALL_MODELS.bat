@echo off
setlocal EnableExtensions
chcp 65001 >nul
cls
echo ================================================================
echo  EMBER - INSTALL ALL OFFLINE MODELS
echo ================================================================
echo WARNING: This pack is approximately 25.4 GB before extra metadata/cache.
echo It may use more disk space while downloading or after model updates.
echo.
choice /C YN /N /M "Install all 8 models? [Y/N]: "
if errorlevel 2 exit /b 1
set "EMBER_BULK_INSTALL=1"

call "%~dp001_Install_Llama_3.2_3B.bat"
call "%~dp002_Install_Qwen_2.5_3B.bat"
call "%~dp003_Install_Qwen_2.5_7B.bat"
call "%~dp004_Install_Qwen_2.5_Coder_3B.bat"
call "%~dp005_Install_Qwen_2.5_Coder_7B.bat"
call "%~dp006_Install_Phi_4_Mini.bat"
call "%~dp007_Install_Gemma_3_4B.bat"
call "%~dp008_Install_Mistral_7B.bat"

echo.
echo [EMBER] All-model install sequence finished.
pause
