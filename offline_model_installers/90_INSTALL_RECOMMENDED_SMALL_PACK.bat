@echo off
setlocal EnableExtensions
chcp 65001 >nul
cls
echo ================================================================
echo  EMBER - RECOMMENDED SMALL OFFLINE MODEL PACK
echo ================================================================
echo This installs approximately 11.6 GB of model data:
echo   Llama 3.2 3B      ~2.0 GB
echo   Qwen 2.5 3B       ~1.9 GB
echo   Qwen Coder 3B     ~1.9 GB
echo   Phi-4 Mini        ~2.5 GB
echo   Gemma 3 4B        ~3.3 GB
echo.
choice /C YN /N /M "Continue? [Y/N]: "
if errorlevel 2 exit /b 1
set "EMBER_BULK_INSTALL=1"

call "%~dp001_Install_Llama_3.2_3B.bat"
call "%~dp002_Install_Qwen_2.5_3B.bat"
call "%~dp004_Install_Qwen_2.5_Coder_3B.bat"
call "%~dp006_Install_Phi_4_Mini.bat"
call "%~dp007_Install_Gemma_3_4B.bat"

echo.
echo [EMBER] Recommended small pack finished.
pause
