param([Parameter(Mandatory = $true)][string]$EmberRoot)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $EmberRoot).Path
$Launcher = Join-Path $Root 'RUN_EMBER.bat'
if (-not (Test-Path -LiteralPath $Launcher)) { throw 'Ember launcher is missing.' }
$Desktop = [Environment]::GetFolderPath('Desktop')
if (-not (Test-Path -LiteralPath $Desktop)) { throw 'Desktop directory is unavailable.' }
$Link = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $Desktop 'Ember.lnk'))
$Link.TargetPath = $Launcher
$Link.WorkingDirectory = $Root
$Link.Description = 'Ember AI - local assistant'
$Icon = Join-Path $Root 'config\ember.ico'
if (Test-Path -LiteralPath $Icon) { $Link.IconLocation = "$Icon,0" }
$Link.Save()
Write-Host '[OK] Ember desktop shortcut created.'
