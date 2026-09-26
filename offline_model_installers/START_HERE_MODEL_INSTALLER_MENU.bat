@echo off
setlocal EnableExtensions
chcp 65001 >nul
:menu
cls
echo ================================================================
echo  EMBER OFFLINE AI MODEL INSTALLER MENU
echo ================================================================
echo  0. Install Ollama runtime
echo  1. Llama 3.2 3B       (~2.0 GB)
echo  2. Qwen 2.5 3B        (~1.9 GB)
echo  3. Qwen 2.5 7B        (~4.7 GB)
echo  4. Qwen Coder 3B      (~1.9 GB)
echo  5. Qwen Coder 7B      (~4.7 GB)
echo  6. Phi-4 Mini         (~2.5 GB)
echo  7. Gemma 3 4B         (~3.3 GB)
echo  8. Mistral 7B         (~4.4 GB)
echo  9. Show installed models
echo  R. Recommended small pack (~11.6 GB)
echo  A. Install all models  (~25.4 GB)
echo  X. Exit
echo ================================================================
echo.
choice /C 0123456789RAX /N /M "Choose: "
set "c=%errorlevel%"
if "%c%"=="13" exit /b 0
if "%c%"=="12" call "%~dp091_INSTALL_ALL_MODELS.bat" & goto menu
if "%c%"=="11" call "%~dp090_INSTALL_RECOMMENDED_SMALL_PACK.bat" & goto menu
if "%c%"=="10" call "%~dp009_CHECK_INSTALLED_MODELS.bat" & goto menu
if "%c%"=="9" call "%~dp008_Install_Mistral_7B.bat" & goto menu
if "%c%"=="8" call "%~dp007_Install_Gemma_3_4B.bat" & goto menu
if "%c%"=="7" call "%~dp006_Install_Phi_4_Mini.bat" & goto menu
if "%c%"=="6" call "%~dp005_Install_Qwen_2.5_Coder_7B.bat" & goto menu
if "%c%"=="5" call "%~dp004_Install_Qwen_2.5_Coder_3B.bat" & goto menu
if "%c%"=="4" call "%~dp003_Install_Qwen_2.5_7B.bat" & goto menu
if "%c%"=="3" call "%~dp002_Install_Qwen_2.5_3B.bat" & goto menu
if "%c%"=="2" call "%~dp001_Install_Llama_3.2_3B.bat" & goto menu
if "%c%"=="1" call "%~dp000_INSTALL_OLLAMA.bat" & goto menu
goto menu
