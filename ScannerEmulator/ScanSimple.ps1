# =============================================================================
# PTM Scanner Emulator - Simple Keyboard Input
# Имитирует USB сканер штрихкодов через SendKeys
# =============================================================================

param(
    [string]$Barcode = ""
)

Add-Type -AssemblyName System.Windows.Forms

function Send-BarcodeAsKeystrokes {
    param([string]$Code)
    
    if ([string]::IsNullOrWhiteSpace($Code)) {
        Write-Host "❌ Штрихкод пустой!" -ForegroundColor Red
        return
    }
    
    # Небольшая задержка для фокусировки окна 1С
    Start-Sleep -Milliseconds 100
    
    # Отправляем посимвольно
    foreach ($char in $Code.ToCharArray()) {
        [System.Windows.Forms.SendKeys]::SendWait($char)
        Start-Sleep -Milliseconds 10
    }
    
    # Enter в конце (как настоящий сканер)
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    
    Write-Host "✅ Отсканировано: $Code" -ForegroundColor Green
}

# Главный блок
if ($Barcode) {
    # Режим командной строки
    Write-Host "🔷 PTM Scanner Emulator" -ForegroundColor Cyan
    Write-Host "Подготовка к отправке..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Send-BarcodeAsKeystrokes -Code $Barcode
} else {
    # Интерактивный режим
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "  PTM Scanner Emulator v1.0" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    
    while ($true) {
        Write-Host "Введите штрихкод (или 'exit' для выхода):" -ForegroundColor Yellow -NoNewline
        $input = Read-Host " "
        
        if ($input -eq "exit" -or $input -eq "q") {
            Write-Host "👋 Выход..." -ForegroundColor Cyan
            break
        }
        
        if ([string]::IsNullOrWhiteSpace($input)) {
            continue
        }
        
        Write-Host "⏳ Через 2 секунды переключитесь на окно 1С..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        
        Send-BarcodeAsKeystrokes -Code $input
        Write-Host ""
    }
}
