<#
.SYNOPSIS
    Мониторинг ошибок 1С через Технологический журнал и Журнал регистрации.
.DESCRIPTION
    Позволяет автоматически отлавливать runtime-ошибки 1С после деплоя.
    Используется на этапе интерактивной отладки (Фаза 4 алгоритма работы агента).
    
    Работает в двух режимах:
    1. Технологический журнал (ТЖ) — ловит EXCP (исключения) в реальном времени
    2. Журнал регистрации (ЖР) — читает ошибки из .lgp файлов базы данных
    
    ВАЖНО: Для ТЖ нужна однократная настройка (Setup) с правами администратора.
    ЖР работает без дополнительной настройки — читает существующие логи.
.PARAMETER Action
    Setup  — Включить ТЖ (настроить logcfg.xml). Нужны права администратора.
    Check  — Прочитать последние ошибки из ТЖ + ЖР.
    Stop   — Выключить ТЖ (удалить logcfg.xml).
    Status — Показать состояние мониторинга.
.PARAMETER LastMinutes
    За сколько последних минут искать ошибки (по умолчанию 30).
.PARAMETER BasePath
    Путь к файловой информационной базе.
.EXAMPLE
    .\monitor-errors.ps1 -Action Setup
    .\monitor-errors.ps1 -Action Check
    .\monitor-errors.ps1 -Action Check -LastMinutes 5
    .\monitor-errors.ps1 -Action Stop
#>

param(
    [ValidateSet("Setup", "Check", "Stop", "Status")]
    [string]$Action = "Check",

    [int]$LastMinutes = 30,
    [string]$BasePath = "D:\Confiq\Public Trade Module"
)

# === НАСТРОЙКИ ===
$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$tjLogDir = Join-Path $scriptDir "logs\tj"

# Путь к журналу регистрации ИБ
$eventLogDir = Join-Path $BasePath "1Cv8Log"

# Поиск 1cv8.exe и conf directory для ТЖ
$v8Dirs = Get-ChildItem "C:\Program Files\1cv8\" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+$' } |
    Sort-Object { [version]$_.Name } -Descending
$confDir = "C:\Program Files\1cv8\conf"
$logcfgPath = Join-Path $confDir "logcfg.xml"

# === УТИЛИТЫ ===

function Write-Mon {
    param([string]$Message, [string]$Status = "INFO")
    $color = switch ($Status) {
        "OK"    { "Green" }
        "FAIL"  { "Red" }
        "WARN"  { "Yellow" }
        "INFO"  { "Cyan" }
        "ERROR" { "Red" }
        default { "White" }
    }
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] [$Status] $Message" -ForegroundColor $color
}

function Read-SharedFile {
    <#
    .DESCRIPTION
        Читает файл, который может быть заблокирован другим процессом (1С).
        Использует FileShare.ReadWrite для совместного доступа.
    #>
    param([string]$Path)
    $fs = $null
    $sr = $null
    try {
        $fs = [System.IO.FileStream]::new(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::ReadWrite
        )
        $sr = [System.IO.StreamReader]::new($fs, [System.Text.Encoding]::UTF8)
        return $sr.ReadToEnd()
    } finally {
        if ($sr) { $sr.Dispose() }
        if ($fs) { $fs.Dispose() }
    }
}

# ═══════════════════════════════════════════════════════════════════
# ACTION: SETUP — Включить Технологический журнал
# ═══════════════════════════════════════════════════════════════════

function Do-Setup {
    Write-Host ""
    Write-Host "========== Настройка мониторинга ошибок ==========" -ForegroundColor Cyan
    Write-Host ""

    # Создать папку для ТЖ логов
    if (-not (Test-Path $tjLogDir)) {
        New-Item -ItemType Directory -Path $tjLogDir -Force | Out-Null
        Write-Mon "Создана папка для ТЖ: $tjLogDir"
    }

    # Генерируем logcfg.xml — только EXCP и EXCPCNTX
    # Расширенный набор событий для полного перехвата ошибок
    # EXCP/EXCPCNTX — runtime-исключения (необработанные)
    # SDBL — ошибки SQL-запросов (блокировки, constraint violations)
    # CALL/SCALL — ошибки клиент-серверных вызовов
    # CONN — ошибки подключений
    # Фильтр по нашей ИБ: processName содержит "Public Trade Module"
    $logcfgContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://v8.1c.ru/v8/tech-log">
    <log location="$tjLogDir" history="24">
        <event>
            <eq property="name" value="EXCP"/>
        </event>
        <event>
            <eq property="name" value="EXCPCNTX"/>
        </event>
        <event>
            <eq property="name" value="SDBL"/>
            <like property="Descr" value="%"/>
        </event>
        <event>
            <eq property="name" value="CALL"/>
            <like property="Descr" value="%"/>
        </event>
        <event>
            <eq property="name" value="SCALL"/>
            <like property="Descr" value="%"/>
        </event>
        <event>
            <eq property="name" value="CONN"/>
            <like property="Descr" value="%"/>
        </event>
        <property name="all"/>
    </log>
</config>
"@

    # Проверяем/создаём conf директорию
    if (-not (Test-Path $confDir)) {
        try {
            New-Item -ItemType Directory -Path $confDir -Force -ErrorAction Stop | Out-Null
        } catch {
            Write-Mon "Не удалось создать $confDir — нужны права администратора" "FAIL"
            Show-ManualSetupInstructions -Content $logcfgContent
            return $false
        }
    }

    # Записываем logcfg.xml
    try {
        [System.IO.File]::WriteAllText($logcfgPath, $logcfgContent, [System.Text.Encoding]::UTF8)
        Write-Mon "logcfg.xml создан: $logcfgPath" "OK"
    } catch {
        Write-Mon "Не удалось записать $logcfgPath — нужны права администратора" "FAIL"
        Show-ManualSetupInstructions -Content $logcfgContent
        return $false
    }

    Write-Host ""
    Write-Mon "Мониторинг ТЖ включён! События: EXCP, EXCPCNTX, SDBL, CALL, SCALL, CONN." "OK"
    Write-Mon "Логи ТЖ: $tjLogDir"
    Write-Host ""
    Write-Host "  ВАЖНО: Перезапустите ВСЕ процессы 1С для активации ТЖ:" -ForegroundColor Yellow
    Write-Host "  - Закрыть конфигуратор и/или предприятие" -ForegroundColor Yellow
    Write-Host "  - Открыть заново" -ForegroundColor Yellow
    Write-Host ""
    return $true
}

function Show-ManualSetupInstructions {
    param([string]$Content)
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "  ║  РУЧНАЯ НАСТРОЙКА (нужны права администратора)  ║" -ForegroundColor Yellow
    Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Вариант 1: Запустить PowerShell от имени администратора:" -ForegroundColor White
    Write-Host "    `$script = Get-ChildItem 'D:\Git\Public_Trade_Module' -Recurse -Filter 'monitor-errors.ps1' | Select -First 1" -ForegroundColor DarkGray
    Write-Host "    powershell -ExecutionPolicy Bypass -File `$script.FullName -Action Setup" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Вариант 2: Создать файл вручную:" -ForegroundColor White
    Write-Host "    Путь: $logcfgPath" -ForegroundColor DarkGray
    Write-Host "    Содержимое:" -ForegroundColor DarkGray
    Write-Host $Content -ForegroundColor DarkGray
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════
# ACTION: CHECK — Прочитать ошибки
# ═══════════════════════════════════════════════════════════════════

function Do-Check {
    Write-Host ""
    Write-Host "========== Проверка ошибок 1С ==========" -ForegroundColor Cyan
    Write-Host "  Период: последние $LastMinutes мин." -ForegroundColor DarkGray
    Write-Host "  ИБ:     $BasePath" -ForegroundColor DarkGray
    Write-Host ""

    $allErrors = @()
    $cutoffTime = (Get-Date).AddMinutes(-$LastMinutes)

    # --- Источник 1: Технологический журнал (EXCP) ---
    $tjErrors = Read-TJErrors -CutoffTime $cutoffTime
    if ($tjErrors.Count -gt 0) {
        $allErrors += $tjErrors
    }

    # --- Источник 2: Журнал регистрации (.lgp) ---
    $eventLogErrors = Read-EventLogErrors -CutoffTime $cutoffTime
    if ($eventLogErrors.Count -gt 0) {
        $allErrors += $eventLogErrors
    }

    # --- Вывод результатов ---
    if ($allErrors.Count -eq 0) {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Mon "Ошибок не обнаружено за последние $LastMinutes мин." "OK"
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        return
    }

    # Структурированный вывод для агента
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "=== НАЙДЕНЫ ОШИБКИ ($($allErrors.Count)) (для Copilot Agent) ===" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""

    $i = 1
    foreach ($err in $allErrors) {
        Write-Host "--- Ошибка [$i] ---" -ForegroundColor Red
        Write-Host "  Источник:  $($err.Source)" -ForegroundColor DarkGray
        Write-Host "  Время:     $($err.Time)" -ForegroundColor DarkGray
        if ($err.Module) {
            Write-Host "  Модуль:    $($err.Module)" -ForegroundColor Yellow
        }
        Write-Host "  Описание:" -ForegroundColor Red
        # Разбиваем длинное описание на строки
        $descLines = $err.Description -split "`n"
        foreach ($line in $descLines) {
            if ($line.Trim()) {
                Write-Host "    $($line.Trim())" -ForegroundColor White
            }
        }
        if ($err.Context) {
            Write-Host "  Контекст:" -ForegroundColor DarkGray
            Write-Host "    $($err.Context)" -ForegroundColor DarkGray
        }
        Write-Host ""
        $i++
    }

    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "=== КОНЕЦ ОШИБОК ===" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Агент ОБЯЗАН:" -ForegroundColor Cyan
    Write-Host "  1. Проанализировать каждую ошибку выше" -ForegroundColor Cyan
    Write-Host "  2. Исправить BSL/XML файлы" -ForegroundColor Cyan
    Write-Host "  3. Запустить deploy-config.ps1 -Action Full" -ForegroundColor Cyan
    Write-Host "  4. Повторить monitor-errors.ps1 -Action Check" -ForegroundColor Cyan
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════
# ЧТЕНИЕ ТЕХНОЛОГИЧЕСКОГО ЖУРНАЛА
# ═══════════════════════════════════════════════════════════════════

function Read-TJErrors {
    param([datetime]$CutoffTime)

    $errors = @()

    if (-not (Test-Path $tjLogDir)) {
        Write-Mon "ТЖ: Папка логов не найдена ($tjLogDir)" "WARN"
        Write-Mon "ТЖ: Запустите: monitor-errors.ps1 -Action Setup" "INFO"
        return $errors
    }

    if (-not (Test-Path $logcfgPath)) {
        Write-Mon "ТЖ: logcfg.xml не найден — мониторинг не настроен" "WARN"
        Write-Mon "ТЖ: Запустите: monitor-errors.ps1 -Action Setup" "INFO"
        return $errors
    }

    # Находим все .log файлы, модифицированные после cutoff
    $logFiles = Get-ChildItem -Path $tjLogDir -Recurse -Filter "*.log" -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -ge $CutoffTime }

    if ($logFiles.Count -eq 0) {
        Write-Mon "ТЖ: Нет свежих логов за последние $LastMinutes мин." "INFO"
        return $errors
    }

    Write-Mon "ТЖ: Анализ $($logFiles.Count) лог-файлов..."

    foreach ($logFile in $logFiles) {
        try {
            $content = Read-SharedFile -Path $logFile.FullName
            $lines = $content -split "`n"

            $currentEventName = ""
            $currentText = ""

            foreach ($line in $lines) {
                # Новое событие: mm:ss.ffffff-duration,EventName,Level,...
                if ($line -match '^(\d{2}:\d{2}\.\d+)-(\d+),(\w+),(\d+),(.*)') {
                    # Сохраняем предыдущее событие с ошибкой
                    if ($currentEventName -in @("EXCP", "SDBL", "CALL", "SCALL", "CONN") -and $currentText) {
                        $err = Parse-TJEvent -EventName $currentEventName -EventText $currentText -LogFile $logFile
                        if ($err) { $errors += $err }
                    }

                    $currentEventName = $Matches[3]
                    $currentText = $line
                } else {
                    # Продолжение многострочного события
                    if ($currentText) {
                        $currentText += "`n$line"
                    }
                }
            }

            # Последнее событие в файле
            if ($currentEventName -in @("EXCP", "SDBL", "CALL", "SCALL", "CONN") -and $currentText) {
                $err = Parse-TJEvent -EventName $currentEventName -EventText $currentText -LogFile $logFile
                if ($err) { $errors += $err }
            }
        } catch {
            Write-Mon "ТЖ: Ошибка чтения $($logFile.Name): $_" "WARN"
        }
    }

    if ($errors.Count -gt 0) {
        Write-Mon "ТЖ: Найдено $($errors.Count) ошибок (EXCP/SDBL/CALL/SCALL/CONN)" "ERROR"
    } else {
        Write-Mon "ТЖ: Ошибок не обнаружено" "OK"
    }

    return $errors
}

function Parse-TJEvent {
    param([string]$EventName, [string]$EventText, $LogFile)

    # Извлекаем Descr (описание ошибки)
    $descr = ""
    if ($EventText -match "Descr='((?:[^']|'')*)'") {
        $descr = $Matches[1] -replace "''", "'"
    } elseif ($EventText -match "Descr=([^,`r`n]+)") {
        $descr = $Matches[1]
    }

    # Для EXCP — Descr обязателен; для SDBL/CALL/SCALL/CONN — ошибочные события всегда имеют Descr
    if (-not $descr) { return $null }

    # Извлекаем processName (путь к базе)
    $processName = ""
    if ($EventText -match "p:processName=([^,`r`n]+)") {
        $processName = $Matches[1]
    }

    # Фильтруем: если processName есть, но НЕ наша база — пропускаем
    if ($processName -and $processName -notmatch "Public.Trade.Module") {
        return $null
    }

    # Извлекаем Module
    $module = ""
    if ($EventText -match "Module=([^,`r`n]+)") {
        $module = $Matches[1]
    }

    # Извлекаем Func (имя функции для CALL/SCALL)
    $func = ""
    if ($EventText -match "Func=([^,`r`n]+)") {
        $func = $Matches[1]
    }

    # Извлекаем Sql (текст запроса для SDBL)
    $sql = ""
    if ($EventName -eq "SDBL" -and $EventText -match "Sql='((?:[^']|'')*)'") {
        $sql = $Matches[1] -replace "''", "'"
        if ($sql.Length -gt 200) { $sql = $sql.Substring(0, 200) + "..." }
    }

    # Время из имени файла: YYMMDDhh.log → дата-час
    $fileTime = ""
    if ($LogFile.Name -match "^(\d{2})(\d{2})(\d{2})(\d{2})") {
        $fileTime = "20$($Matches[1])-$($Matches[2])-$($Matches[3]) $($Matches[4]):xx"
    }

    # Точное время из события: mm:ss.ffffff
    $eventTime = ""
    if ($EventText -match "^(\d{2}:\d{2}\.\d+)") {
        $eventTime = $Matches[1]
    }

    # Формируем контекст
    $contextParts = @()
    if ($processName) { $contextParts += $processName }
    if ($func) { $contextParts += "Func=$func" }
    if ($sql) { $contextParts += "SQL: $sql" }
    $context = $contextParts -join " | "

    return @{
        Source      = "ТЖ ($EventName)"
        Time        = "$fileTime $eventTime".Trim()
        Module      = $module
        Description = $descr
        Context     = $context
    }
}

# ═══════════════════════════════════════════════════════════════════
# ЧТЕНИЕ ЖУРНАЛА РЕГИСТРАЦИИ (.lgp)
# ═══════════════════════════════════════════════════════════════════

function Read-EventLogErrors {
    param([datetime]$CutoffTime)

    $errors = @()

    if (-not (Test-Path $eventLogDir -ErrorAction SilentlyContinue)) {
        Write-Mon "ЖР: Папка журнала регистрации не найдена ($eventLogDir)" "WARN"
        return $errors
    }

    # Находим .lgp файлы
    $lgpFiles = Get-ChildItem -Path $eventLogDir -Filter "*.lgp" -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending

    if ($lgpFiles.Count -eq 0) {
        Write-Mon "ЖР: Нет файлов .lgp" "WARN"
        return $errors
    }

    # Читаем словарь (lgf) для расшифровки кодов событий
    $lgfPath = Join-Path $eventLogDir "1Cv8.lgf"
    $eventDict = @{}
    if (Test-Path $lgfPath) {
        try {
            $lgfContent = Read-SharedFile -Path $lgfPath
            # Парсим записи вида {4,"_$Session$_.Start",2} — код/тип, имя, номер
            $dictMatches = [regex]::Matches($lgfContent, '\{4,"([^"]+)",(\d+)\}')
            foreach ($m in $dictMatches) {
                $eventDict[$m.Groups[2].Value] = $m.Groups[1].Value
            }
        } catch {
            Write-Mon "ЖР: Ошибка чтения словаря 1Cv8.lgf: $_" "WARN"
        }
    }

    Write-Mon "ЖР: Анализ $($lgpFiles.Count) файлов журнала..."

    # Формируем cutoff в формате 1С: YYYYMMDDHHmmss
    $cutoffStr = $CutoffTime.ToString("yyyyMMddHHmmss")

    foreach ($lgpFile in $lgpFiles) {
        try {
            $content = Read-SharedFile -Path $lgpFile.FullName

            # Разбираем записи: каждая запись начинается с {YYYYMMDDHHmmss,
            # Формат записи lgp v2.0:
            # {datetime,TransactionStatus,{TransactionNum,TransactionDate},
            #  UserCode,ComputerCode,AppCode,Port,EventCode,Severity,
            #  Comment,Data,...}
            #
            # Severity: I=Info, W=Warning, E=Error, N=Note

            # Ищем записи с severity E (Error) или W (Warning для полноты)
            # Паттерн: после EventCode идёт ,E, или ,W,
            $records = [regex]::Matches($content, '\{(\d{14}),\w,\s*\{[^}]*\},(\d+),(\d+),(\d+),(\d+),(\d+),([EWIN]),"([^"]*)"')

            foreach ($record in $records) {
                $dateStr = $record.Groups[1].Value
                $severity = $record.Groups[7].Value
                $comment = $record.Groups[8].Value

                # Только ошибки (E) и предупреждения (W) — для полноты отладки
                if ($severity -notin @("E", "W")) { continue }

                # Фильтр по времени
                if ($dateStr -lt $cutoffStr) { continue }

                # Форматируем дату для вывода
                $displayDate = ""
                if ($dateStr -match "(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})") {
                    $displayDate = "$($Matches[1])-$($Matches[2])-$($Matches[3]) $($Matches[4]):$($Matches[5]):$($Matches[6])"
                }

                # Определяем событие по коду
                $eventCode = $record.Groups[6].Value
                $eventName = if ($eventDict.ContainsKey($eventCode)) { $eventDict[$eventCode] } else { "Event#$eventCode" }

                # Определяем уровень серьёзности для отображения
                $severityText = switch ($severity) {
                    "E" { "ОШИБКА" }
                    "W" { "ПРЕДУПР" }
                    default { $severity }
                }

                # Извлекаем дополнительные данные после Comment
                # В lgp после Comment идёт ,DataSize,Data,...
                $description = $comment
                if (-not $description) {
                    $description = "Ошибка в событии: $eventName"
                }

                $errors += @{
                    Source      = "ЖР ($eventName) [$severityText]"
                    Time        = $displayDate
                    Module      = ""
                    Description = $description
                    Context     = ""
                }
            }
        } catch {
            Write-Mon "ЖР: Ошибка чтения $($lgpFile.Name): $_" "WARN"
        }
    }

    if ($errors.Count -gt 0) {
        Write-Mon "ЖР: Найдено $($errors.Count) ошибок" "ERROR"
    } else {
        Write-Mon "ЖР: Ошибок не обнаружено" "OK"
    }

    return $errors
}

# ═══════════════════════════════════════════════════════════════════
# ACTION: STOP — Выключить ТЖ
# ═══════════════════════════════════════════════════════════════════

function Do-Stop {
    Write-Host ""
    Write-Host "========== Остановка мониторинга ТЖ ==========" -ForegroundColor Cyan
    Write-Host ""

    if (Test-Path $logcfgPath) {
        try {
            Remove-Item $logcfgPath -Force -ErrorAction Stop
            Write-Mon "logcfg.xml удалён: $logcfgPath" "OK"
            Write-Host ""
            Write-Host "  ТЖ отключён. Перезапустите 1С для вступления в силу." -ForegroundColor Yellow
        } catch {
            Write-Mon "Не удалось удалить $logcfgPath — нужны права администратора" "FAIL"
        }
    } else {
        Write-Mon "logcfg.xml не найден — ТЖ не был настроен" "INFO"
    }

    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════
# ACTION: STATUS — Состояние мониторинга
# ═══════════════════════════════════════════════════════════════════

function Do-Status {
    Write-Host ""
    Write-Host "========== Состояние мониторинга ==========" -ForegroundColor Cyan
    Write-Host ""

    # --- ТЖ ---
    Write-Host "  Технологический журнал (ТЖ):" -ForegroundColor White
    if (Test-Path $logcfgPath) {
        Write-Mon "  logcfg.xml АКТИВЕН ($logcfgPath)" "OK"
        if (Test-Path $tjLogDir) {
            $logFiles = Get-ChildItem -Path $tjLogDir -Recurse -Filter "*.log" -ErrorAction SilentlyContinue
            $logSize = $logFiles | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue
            $sizeMB = [math]::Round(($logSize.Sum / 1MB), 2)
            Write-Mon "  Логи: $sizeMB MB ($($logSize.Count) файлов)" "INFO"

            # Последний лог
            $lastLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($lastLog) {
                Write-Mon "  Последний: $($lastLog.Name) ($($lastLog.LastWriteTime))" "INFO"
            }
        }
    } else {
        Write-Mon "  НЕ настроен (logcfg.xml отсутствует)" "WARN"
        Write-Host "    Запустите: monitor-errors.ps1 -Action Setup" -ForegroundColor Cyan
    }

    Write-Host ""

    # --- ЖР ---
    Write-Host "  Журнал регистрации (ЖР):" -ForegroundColor White
    if (Test-Path $eventLogDir) {
        $lgpFiles = Get-ChildItem -Path $eventLogDir -Filter "*.lgp" -ErrorAction SilentlyContinue
        $lgfExists = Test-Path (Join-Path $eventLogDir "1Cv8.lgf")
        Write-Mon "  Папка: $eventLogDir" "OK"
        Write-Mon "  Файлов .lgp: $($lgpFiles.Count), словарь .lgf: $(if ($lgfExists) {'есть'} else {'нет'})" "INFO"

        $lastLgp = $lgpFiles | Sort-Object Name -Descending | Select-Object -First 1
        if ($lastLgp) {
            $sizeKB = [math]::Round($lastLgp.Length / 1KB)
            Write-Mon "  Последний: $($lastLgp.Name) ($sizeKB KB)" "INFO"
        }
    } else {
        Write-Mon "  Папка журнала не найдена ($eventLogDir)" "WARN"
    }

    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "========== PTM Error Monitor: $Action ==========" -ForegroundColor Cyan
Write-Host "========== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==========" -ForegroundColor DarkGray
Write-Host ""

switch ($Action) {
    "Setup"  { Do-Setup }
    "Check"  { Do-Check }
    "Stop"   { Do-Stop }
    "Status" { Do-Status }
}
