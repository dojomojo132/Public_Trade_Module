# =========================================================
# Драйвер: COM -> CLIPBOARD (STA MODE FIXED)
# =========================================================

# 1. Проверка режима запуска (Нам нужен STA для работы с буфером)
if ($host.Runspace.ApartmentState -ne 'STA') {
    Write-Host "Перезапуск в режиме STA..." -ForegroundColor Cyan
    # Перезапускаем сами себя с флагом -STA
    powershell.exe -NoProfile -STA -File $MyInvocation.MyCommand.Path
    Exit
}

# 2. Настройки
$portName = "COM11"     # <--- ВАШ ПОРТ
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.IO.Ports

# 3. Подключение
Write-Host "--- PTM Driver (Clipboard) ---" -ForegroundColor Cyan

Try {
    $port = New-Object System.IO.Ports.SerialPort
    $port.PortName = $portName
    $port.BaudRate = 9600
    $port.Parity   = [System.IO.Ports.Parity]::None
    $port.DataBits = 8
    $port.StopBits = [System.IO.Ports.StopBits]::One
    
    $port.Open()
    Write-Host "[OK] Порт $portName открыт." -ForegroundColor Green
}
Catch {
    Write-Host "[ERROR] Ошибка порта: $_" -ForegroundColor Red
    Write-Host "Нажмите Enter для выхода..."
    Read-Host
    Exit
}

# 4. Цикл
While ($true) {
    Try {
        if ($port.IsOpen) {
            $barcode = $port.ReadLine()
            
            If (-not [string]::IsNullOrWhiteSpace($barcode)) {
                $barcode = $barcode.Trim()
                Write-Host "ШК: $barcode" -ForegroundColor Yellow
                
                # Запись в буфер
                [System.Windows.Forms.Clipboard]::SetText("///SCAN:$barcode")
            }
        }
    }
    Catch {
        # Игнорируем мелкие ошибки
    }
}