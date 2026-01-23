# =============================================================================
# PTM Scanner Emulator - Batch Test Script
# Автоматическое тестирование списка штрихкодов
# =============================================================================

param(
    [string]$TestFile = "test-barcodes.txt",
    [int]$DelaySeconds = 3
)

if (-not (Test-Path $TestFile)) {
    Write-Host "❌ Файл $TestFile не найден!" -ForegroundColor Red
    exit 1
}

$barcodes = Get-Content $TestFile | Where-Object { 
    $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' 
}

if ($barcodes.Count -eq 0) {
    Write-Host "❌ В файле нет штрихкодов!" -ForegroundColor Red
    exit 1
}

Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PTM Scanner - Пакетное тестирование" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Найдено штрихкодов: $($barcodes.Count)" -ForegroundColor Yellow
Write-Host "Задержка между сканами: $DelaySeconds сек" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏳ Через 5 секунд начнётся тестирование..." -ForegroundColor Green
Write-Host "ПЕРЕКЛЮЧИТЕСЬ НА ОКНО 1С!" -ForegroundColor Red
Write-Host ""

Start-Sleep -Seconds 5

$counter = 1
foreach ($barcode in $barcodes) {
    Write-Host "[$counter/$($barcodes.Count)] Сканирование: $barcode" -ForegroundColor Cyan
    
    & "$PSScriptRoot\ScanSimple.ps1" -Barcode $barcode
    
    if ($counter -lt $barcodes.Count) {
        Start-Sleep -Seconds $DelaySeconds
    }
    
    $counter++
}

Write-Host ""
Write-Host "✅ Тестирование завершено!" -ForegroundColor Green
Write-Host "Отсканировано: $($barcodes.Count) штрихкодов" -ForegroundColor Yellow
