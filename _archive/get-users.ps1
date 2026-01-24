# Получить список пользователей 1С базы

$ErrorActionPreference = "Stop"

try {
    Write-Host "Подключение к 1С..." -ForegroundColor Yellow
    
    $v83 = New-Object -ComObject "V83.COMConnector"
    
    # Подключаемся без пользователя
    $connString = 'File="D:\Confiq\Public Trade Module";'
    Write-Host "Строка подключения: $connString" -ForegroundColor Cyan
    
    $conn = $v83.Connect($connString)
    
    Write-Host "`nПодключение успешно!" -ForegroundColor Green
    Write-Host "`nПользователи информационной базы:" -ForegroundColor Yellow
    
    $users = $conn.InfoBaseUsers
    $count = 0
    
    foreach($user in $users.GetUsers()) {
        $count++
        Write-Host "  $count. $($user.Name)" -ForegroundColor White
    }
    
    if ($count -eq 0) {
        Write-Host "  (нет пользователей)" -ForegroundColor Gray
    }
    
    Write-Host "`nВсего пользователей: $count" -ForegroundColor Green
    
} catch {
    Write-Host "`nОшибка: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
