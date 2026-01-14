# =============================================================================
# Драйвер-мост: COM -> Клавиатура (SAFE MODE)
# =============================================================================

# --- НАСТРОЙКИ ---
$portName = "COM11"      # <--- ВАШ ПОРТ
$baudRate = 9600
$focusKey = "{F7}"
# -----------------

Clear-Host
Write-Host "--- Запуск драйвера PTM ---" -ForegroundColor Cyan

# 1. Загрузка библиотек
Try {
    Add-Type -AssemblyName System.IO.Ports
    Add-Type -AssemblyName System.Windows.Forms
}
Catch {
    Write-Host "[FATAL] Ошибка загрузки библиотек .NET: $_" -ForegroundColor Red
    Read-Host "Enter для выхода..."
    Exit
}

# 2. Безопасное создание объекта (пошагово)
Try {
    $port = New-Object System.IO.Ports.SerialPort
    $port.PortName = $portName
    $port.BaudRate = $baudRate
    $port.Parity   = [System.IO.Ports.Parity]::None
    $port.DataBits = 8
    $port.StopBits = [System.IO.Ports.StopBits]::One
}
Catch {
    Write-Host "[FATAL] Не удалось создать объект SerialPort. Проверьте версию PowerShell." -ForegroundColor Red
    Write-Host "Ошибка: $_" -ForegroundColor Red
    Read-Host "Enter для выхода..."
    Exit
}

# 3. Открытие порта
Try {
    $port.Open()
    Write-Host "[OK] Порт $portName успешно открыт." -ForegroundColor Green
    Write-Host "[INFO] Режим: $focusKey -> ШК -> Enter" -ForegroundColor Gray
    Write-Host "[INFO] Ожидание сканирования... (Ctrl+C для выхода)" -ForegroundColor Yellow
}
Catch {
    Write-Host "[ERROR] ОШИБКА ОТКРЫТИЯ ПОРТА $portName" -ForegroundColor Red
    Write-Host "Причина: $_" -ForegroundColor Red
    Write-Host "--------------------------------------------------------" -ForegroundColor Gray
    Write-Host "СОВЕТЫ:" -ForegroundColor White
    Write-Host "1. Проверьте Диспетчер устройств: точно ли сканер на $portName?"
    Write-Host "2. Закройте другие программы, которые могут занимать порт (например, 1С, драйвер Атол)."
    Write-Host "3. Выдерните и вставьте сканер в USB."
    Write-Host "--------------------------------------------------------" -ForegroundColor Gray
    Read-Host "Нажмите Enter для выхода..."
    Exit
}

# 4. Основной цикл
While ($true) {
    Try {
        if ($port.IsOpen) {
            $barcode = $port.ReadLine()
            
            If (-not [string]::IsNullOrWhiteSpace($barcode)) {
                $barcode = $barcode.Trim()
                Write-Host "ШК: $barcode" -ForegroundColor Green -NoNewline
                
                # Эмуляция
                [System.Windows.Forms.SendKeys]::SendWait($focusKey)
                Start-Sleep -Milliseconds 50
                [System.Windows.Forms.SendKeys]::SendWait($barcode)
                [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
                
                Write-Host " -> 1C" -ForegroundColor Cyan
            }
        }
    }
    Catch {
        # Игнорируем ошибки чтения (таймауты)
    }
}