param(
    [Parameter(Mandatory=$true)][string]$Model,
    [Parameter(Mandatory=$true)][string]$EmberRoot
)
$ErrorActionPreference = 'Stop'
$config = Join-Path $EmberRoot 'config\api_keys.json'
if (-not (Test-Path $config)) {
    throw "Ember config not found: $config"
}
$obj = Get-Content -LiteralPath $config -Raw | ConvertFrom-Json
$obj.llm_provider = 'ollama'
$obj.llm_url = 'http://localhost:11434'
$obj.llm_model = $Model
if ($null -eq $obj.llm_max_tokens) { $obj | Add-Member -NotePropertyName llm_max_tokens -NotePropertyValue 768 }
if ($null -eq $obj.llm_temperature) { $obj | Add-Member -NotePropertyName llm_temperature -NotePropertyValue 0.35 }
$obj | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $config -Encoding UTF8
