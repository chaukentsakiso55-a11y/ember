@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $desk=[Environment]::GetFolderPath('Desktop'); $lnk=$ws.CreateShortcut((Join-Path $desk 'Ember.lnk')); $lnk.TargetPath=(Join-Path $PWD 'RUN_EMBER.bat'); $lnk.WorkingDirectory=$PWD; $lnk.IconLocation=(Join-Path $PWD 'assets\ember.ico'); $lnk.Description='Ember Neural Command Node'; $lnk.Save()"
if errorlevel 1 (echo Could not create the shortcut.& exit /b 1)
echo Ember desktop icon created.
exit /b 0
