# --- НАЧАЛО СКРИПТА ---

# 1. Перезапуск в режиме STA (обязательно для буфера обмена)
if ($host.Runspace.ApartmentState -ne 'STA') {
    powershell.exe -NoProfile -STA -File $MyInvocation.MyCommand.Path
    Exit
}

# 2. Загрузка библиотек
[void][System.Reflection.Assembly]::LoadWithPartialName("System.IO.Ports")
[void][System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")

# 3. Настройки
$portName = "COM11"
$baudRate = 9600

Write-Host "--- PTM Driver (Clipboard) ---" -ForegroundColor Cyan

# 4. Открытие порта
Try {
    $port = New-Object System.IO.Ports.SerialPort
    $port.PortName = $portName
    $port.BaudRate = $baudRate
    $port.Parity   = [System.IO.Ports.Parity]::None
    $port.DataBits = 8
    $port.StopBits = [System.IO.Ports.StopBits]::One
    
    $port.Open()
    Write-Host "[OK] Порт $portName открыт." -ForegroundColor Green
}
Catch {
    Write-Host "[ERROR] Ошибка открытия порта!" -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода..."
    Exit
}

# 5. Главный цикл
While ($true) {
    Try {
        if ($port.IsOpen) {
            # Читаем данные
            $barcode = $port.ReadLine()
            
            # Если данные есть - пишем в буфер
            If (-not [string]::IsNullOrWhiteSpace($barcode)) {
                $barcode = $barcode.Trim()
                Write-Host "ШК: $barcode" -ForegroundColor Yellow
                
                [System.Windows.Forms.Clipboard]::SetText("///SCAN:$barcode")
            }
        }
    }
    Catch {
        # Игнорируем ошибки чтения
    }
}

# --- КОНЕЦ СКРИПТА ---