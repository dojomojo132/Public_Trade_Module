# Запуск Grok с MCP-профилем только для Public_Trade_Module (PTM_Clean).
# Использование:
#   .\scripts\Start-Grok.ps1
#   .\scripts\Start-Grok.ps1 -Profile minimal
#   .\scripts\Start-Grok.ps1 -Profile debug -Bootstrap
#   .\scripts\Start-Grok.ps1 -Profile standard -NoLaunch

param(
    [ValidateSet("minimal", "standard", "debug", "full", "extras")]
    [string]$McpProfile = "standard",
    [switch]$Bootstrap,
    [switch]$NoPlugins,
    [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Error "Не найден venv: $Python"
}

Write-Host "Project: $ProjectRoot"
Write-Host "Profile: $McpProfile"

$applyArgs = @("scripts\mcp_apply_profile.py", $McpProfile)
if ($NoPlugins) { $applyArgs += "--no-plugins" }
& $Python @applyArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Bootstrap) {
    & $Python scripts\project_bootstrap.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host ""
Write-Host "Проверка MCP (должны быть только серверы PTM):"
grok mcp list

if (-not $NoLaunch) {
    Write-Host ""
    Write-Host "Запуск Grok из $ProjectRoot ..."
    grok
}