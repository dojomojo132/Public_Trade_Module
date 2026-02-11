<#
.SYNOPSIS
    Загрузка, проверка и запуск конфигурации 1С:Предприятие 8.3
.DESCRIPTION
    Полный цикл: валидация XML → загрузка в ИБ → синтакс-контроль → обновление БД → запуск
    Предназначен для автоматизации через Copilot Agent.
    
    ВАЖНО: При ошибках выводит структурированный блок === ОШИБКИ (для Copilot Agent) ===
    который агент ОБЯЗАН разобрать (парсить) и исправить все перечисленные проблемы.
.PARAMETER Action
    Действие: Load, Check, Update, Run, Full (все шаги), Info, Designer
.PARAMETER BasePath
    Путь к файловой информационной базе
.PARAMETER ConfigPath
    Путь к XML-файлам конфигурации
.PARAMETER User
    Имя пользователя ИБ (по умолчанию Admin)
.PARAMETER Password
    Пароль пользователя ИБ
.PARAMETER TimeoutSeconds
    Таймаут выполнения каждой операции 1С (по умолчанию 300 секунд)
.EXAMPLE
    .\deploy-config.ps1 -Action Full
    .\deploy-config.ps1 -Action Load
    .\deploy-config.ps1 -Action Check
    .\deploy-config.ps1 -Action Run
    .\deploy-config.ps1 -Action Designer
#>

param(
    [ValidateSet("Load", "Check", "Update", "Run", "Designer", "Full", "Info")]
    [string]$Action = "Full",

    [string]$BasePath = "D:\Confiq\Public Trade Module",
    [string]$ConfigPath = "",
    [string]$User = "",
    [string]$Password = "",
    [string]$LogDir = "",
    [int]$TimeoutSeconds = 300
)

# === НАСТРОЙКИ ===
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $projectRoot "Конфигурация\Проверка"
}
if (-not $LogDir) {
    $LogDir = Join-Path $projectRoot "Документация\Валидация\logs"
}

# Поиск 1cv8.exe
$v8Dirs = Get-ChildItem "C:\Program Files\1cv8\" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+$' } |
    Sort-Object { [version]$_.Name } -Descending
$v8exe = $null
foreach ($dir in $v8Dirs) {
    $candidate = Join-Path $dir.FullName "bin\1cv8.exe"
    if (Test-Path $candidate) {
        $v8exe = $candidate
        break
    }
}

# === ФУНКЦИИ ===

function Write-Step {
    param([string]$Step, [string]$Message, [string]$Status = "INFO")
    $color = switch ($Status) {
        "OK"    { "Green" }
        "FAIL"  { "Red" }
        "WARN"  { "Yellow" }
        "INFO"  { "Cyan" }
        default { "White" }
    }
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] [$Status] $Step - $Message" -ForegroundColor $color
}

function Read-LogWithEncoding {
    <#
    .DESCRIPTION
        Читает лог-файл 1С, пробуя несколько кодировок (UTF-8 BOM, UTF-8, Windows-1251, Default)
    #>
    param([string]$Path)
    if (-not (Test-Path $Path)) { return "" }

    # Попытка 1: UTF-8 (стандарт 1С)
    try {
        $content = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
        if ($content -and $content.Trim()) { return $content }
    } catch {}

    # Попытка 2: Windows-1251 (некоторые версии 1С)
    try {
        $enc1251 = [System.Text.Encoding]::GetEncoding(1251)
        $content = [System.IO.File]::ReadAllText($Path, $enc1251)
        if ($content -and $content.Trim()) { return $content }
    } catch {}

    # Попытка 3: Default (системная кодировка)
    try {
        $content = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::Default)
        if ($content -and $content.Trim()) { return $content }
    } catch {}

    return ""
}

function Invoke-1C {
    <#
    .DESCRIPTION
        Запускает 1cv8.exe с аргументами, захватывает stdout, stderr, лог-файл.
        Добавлен таймаут для защиты от зависаний на диалогах.
    #>
    param(
        [string]$Mode,          # DESIGNER или ENTERPRISE
        [string[]]$ExtraArgs,
        [int]$Timeout = $TimeoutSeconds
    )

    if (-not $v8exe -or -not (Test-Path $v8exe)) {
        Write-Step "1cv8" "1cv8.exe не найден!" "FAIL"
        return @{ ExitCode = -1; Log = ""; Stdout = ""; Stderr = "1cv8.exe не найден"; LogFile = ""; TimedOut = $false; AllOutput = "ОШИБКА: 1cv8.exe не найден" }
    }

    # Создать папку логов
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }

    $logFile = Join-Path $LogDir ("1c-{0}-{1}.log" -f $Mode.ToLower(), (Get-Date -Format "yyyyMMdd-HHmmss"))

    $allArgs = @($Mode, "/F", "`"$BasePath`"")
    if ($User) { $allArgs += @("/N", "`"$User`"") }
    if ($Password) { $allArgs += @("/P", "`"$Password`"") }
    $allArgs += $ExtraArgs
    $allArgs += @("/DisableStartupDialogs", "/DisableStartupMessages")
    $allArgs += @("/Out", "`"$logFile`"")

    $argString = $allArgs -join " "
    Write-Step "1cv8" "Команда: 1cv8.exe $argString"
    Write-Step "1cv8" "Таймаут: $Timeout сек." "INFO"

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $v8exe
    $psi.Arguments = $argString
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    $process = [System.Diagnostics.Process]::Start($psi)

    # Асинхронное чтение stdout/stderr для предотвращения deadlock
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()

    $timedOut = $false
    $exited = $process.WaitForExit($Timeout * 1000)
    if (-not $exited) {
        $timedOut = $true
        Write-Step "1cv8" "ТАЙМАУТ $Timeout сек. — процесс завис (вероятно диалоговое окно). Завершаем принудительно." "FAIL"
        try { $process.Kill() } catch {}
        Start-Sleep -Milliseconds 500
    }

    $stdout = ""
    $stderr = ""
    try { $stdout = $stdoutTask.Result } catch {}
    try { $stderr = $stderrTask.Result } catch {}

    # Читаем лог с поддержкой нескольких кодировок
    $logContent = Read-LogWithEncoding -Path $logFile

    # Собираем ВСЕ доступные данные в одну строку для парсинга
    $allOutput = @()
    if ($logContent) { $allOutput += "=LOG= $logContent" }
    if ($stdout) { $allOutput += "=STDOUT= $stdout" }
    if ($stderr) { $allOutput += "=STDERR= $stderr" }
    if ($timedOut) { $allOutput += "=TIMEOUT= Процесс 1С завис и был завершён принудительно через $Timeout сек. Вероятная причина: 1С пытается показать диалог с ошибкой." }
    $allOutputStr = $allOutput -join "`n"

    $exitCode = if ($timedOut) { -2 } else { $process.ExitCode }

    return @{
        ExitCode  = $exitCode
        Log       = $logContent
        Stdout    = $stdout
        Stderr    = $stderr
        LogFile   = $logFile
        TimedOut  = $timedOut
        AllOutput = $allOutputStr
    }
}

function Parse-1CErrors {
    <#
    .DESCRIPTION
        Парсит ошибки из всех источников (лог, stdout, stderr).
        При ExitCode != 0 ВСЕ непустые строки считаются значимыми.
    #>
    param(
        [string]$LogContent,
        [string]$Stdout = "",
        [string]$Stderr = "",
        [bool]$OperationFailed = $false
    )

    $errors = @()
    $warnings = @()

    # Собираем всё в один текст
    $allText = @($LogContent, $Stdout, $Stderr) | Where-Object { $_ } | ForEach-Object { $_.Trim() }
    $fullText = $allText -join "`n"

    if (-not $fullText) {
        if ($OperationFailed) {
            $errors += "[ПУСТОЙ ЛОГ] Операция завершилась с ошибкой, но лог-файл пуст. Возможные причины: проблема с правами доступа, путь к ИБ или конфигурации некорректен."
        }
        return @{ Errors = $errors; Warnings = $warnings }
    }

    $lines = $fullText -split "`n"

    # Паттерны критических ошибок (ВСЕГДА ошибка)
    $errorPatterns = @(
        "ошибк",        # ошибка, ошибки
        "error",
        "неверн",       # неверный, неверное
        "невалидн",     # невалидный
        "не найден",    # не найдено, не найден
        "отсутствует",
        "не удалось",
        "unable",
        "failed",
        "fatal",
        "critical",
        "exception",
        "нарушение",    # нарушение целостности
        "недопустим",   # недопустимый
        "не распознан", # не распознано
        "некорректн",   # некорректный
        "не соответствует",
        "дублирован",   # дублированный UUID
        "confliciting",
        "duplicate"
    )

    # Паттерны "тихих" ошибок (1С заблокировала диалог)
    $dialogBlockedPatterns = @(
        "запрещено использование окон",
        "DisableStartupDialogs"
    )

    # Паттерн ошибок в формате 1С: {Модуль(строка, колонка)}: текст ошибки
    $v8ErrorLinePattern = "^\{.*\}"

    $hasDialogBlocked = $false

    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if (-not $trimmed) { continue }

        # Проверка: 1С заблокировала диалог
        $isDialogBlocked = $false
        foreach ($dp in $dialogBlockedPatterns) {
            if ($trimmed -match [regex]::Escape($dp)) {
                $isDialogBlocked = $true
                $hasDialogBlocked = $true
                break
            }
        }

        if ($isDialogBlocked) {
            # НЕ пропускаем! Это критическая информация
            $errors += "[ДИАЛОГ ЗАБЛОКИРОВАН] $trimmed"
            continue
        }

        # Проверка: ошибка в формате 1С
        if ($trimmed -match $v8ErrorLinePattern) {
            $errors += $trimmed
            continue
        }

        # Проверка по паттернам
        $isError = $false
        foreach ($pattern in $errorPatterns) {
            if ($trimmed -match $pattern) {
                $isError = $true
                break
            }
        }

        if ($isError) {
            $errors += $trimmed
        } elseif ($OperationFailed) {
            # При провале операции — ВСЕ строки значимы как контекст
            $warnings += $trimmed
        }
    }

    # Если обнаружен заблокированный диалог — добавить объяснение для агента
    if ($hasDialogBlocked) {
        $errors += "[ДИАГНОЗ] 1С попыталась показать диалоговое окно с ошибкой, но флаг /DisableStartupDialogs заблокировал его. Это означает КРИТИЧЕСКУЮ ошибку в XML-структуре конфигурации. Запусти validate-config.ps1 и проверь XML-файлы."
    }

    # Если операция провалилась, но ни одной ошибки не нашли в тексте
    if ($OperationFailed -and $errors.Count -eq 0) {
        $errors += "[НЕ РАСПОЗНАНО] Операция завершилась с ошибкой, но парсер не смог извлечь конкретные ошибки из лога. Полное содержимое лога (ниже) требует ручного анализа."
    }

    return @{ Errors = $errors; Warnings = $warnings }
}

function Format-ErrorBlockForAgent {
    <#
    .DESCRIPTION
        Формирует структурированный блок ошибок для Copilot Agent.
        Агент ОБЯЗАН разобрать этот блок и исправить все перечисленные проблемы.
    #>
    param(
        [string]$Stage,          # Этап: "ЗАГРУЗКА", "СИНТАКС-КОНТРОЛЬ", "ОБНОВЛЕНИЕ_БД"
        [int]$ExitCode,
        [string[]]$Errors,
        [string[]]$Warnings,
        [string]$RawLog,
        [string]$LogFile,
        [string]$Stdout,
        [string]$Stderr,
        [bool]$TimedOut = $false
    )

    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "=== ОШИБКИ (для Copilot Agent) ===" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "ЭТАП: $Stage" -ForegroundColor Red
    Write-Host "EXIT_CODE: $ExitCode" -ForegroundColor Red
    if ($TimedOut) {
        Write-Host "ТАЙМАУТ: ДА — процесс 1С завис и был принудительно завершён" -ForegroundColor Red
    }
    Write-Host "LOG_FILE: $LogFile" -ForegroundColor Red
    Write-Host ""

    # --- Ошибки ---
    if ($Errors -and $Errors.Count -gt 0) {
        Write-Host "--- ОШИБКИ ($($Errors.Count)) ---" -ForegroundColor Red
        $i = 1
        foreach ($err in $Errors) {
            Write-Host "  [$i] $err" -ForegroundColor Red
            $i++
        }
        Write-Host ""
    }

    # --- Предупреждения ---
    if ($Warnings -and $Warnings.Count -gt 0) {
        Write-Host "--- ПРЕДУПРЕЖДЕНИЯ ($($Warnings.Count)) ---" -ForegroundColor Yellow
        foreach ($w in $Warnings) {
            Write-Host "  $w" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    # --- Сырой лог (ВСЕГДА выводим при ошибке) ---
    Write-Host "--- ПОЛНЫЙ ЛОГ 1С ---" -ForegroundColor DarkGray
    if ($RawLog -and $RawLog.Trim()) {
        Write-Host $RawLog
    } else {
        Write-Host "  (лог пуст)"
    }
    Write-Host "--- КОНЕЦ ЛОГА ---" -ForegroundColor DarkGray

    # --- Stdout/Stderr (если есть) ---
    if ($Stdout -and $Stdout.Trim()) {
        Write-Host ""
        Write-Host "--- STDOUT ---" -ForegroundColor DarkGray
        Write-Host $Stdout
        Write-Host "--- КОНЕЦ STDOUT ---" -ForegroundColor DarkGray
    }
    if ($Stderr -and $Stderr.Trim()) {
        Write-Host ""
        Write-Host "--- STDERR ---" -ForegroundColor DarkGray
        Write-Host $Stderr
        Write-Host "--- КОНЕЦ STDERR ---" -ForegroundColor DarkGray
    }

    Write-Host ""
    Write-Host "--- ТРЕБУЕМЫЕ ДЕЙСТВИЯ ---" -ForegroundColor Cyan
    Write-Host "  Агент ОБЯЗАН:" -ForegroundColor Cyan
    Write-Host "  1. Проанализировать ВСЕ ошибки выше" -ForegroundColor Cyan
    Write-Host "  2. Исправить XML/BSL файлы" -ForegroundColor Cyan
    Write-Host "  3. Запустить deploy-config.ps1 -Action Full повторно" -ForegroundColor Cyan
    Write-Host "  4. Повторять пока Deploy не завершится УСПЕШНО" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "=== КОНЕЦ ОШИБОК ===" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
}

# === ДЕЙСТВИЯ ===

function Show-Info {
    Write-Host ""
    Write-Host "========== PTM Deploy Config ==========" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1cv8.exe:    $v8exe"
    Write-Host "  ИБ:          $BasePath"
    Write-Host "  Исходники:   $ConfigPath"
    Write-Host "  Логи:        $LogDir"
    Write-Host "  Пользователь: $User"
    Write-Host "  Таймаут:     $TimeoutSeconds сек."
    Write-Host ""

    if ($v8exe -and (Test-Path $v8exe)) {
        Write-Step "1cv8" "Платформа найдена: $v8exe" "OK"
    } else {
        Write-Step "1cv8" "Платформа не найдена!" "FAIL"
    }

    if (Test-Path $BasePath) {
        Write-Step "ИБ" "Информационная база существует" "OK"
    } else {
        Write-Step "ИБ" "Информационная база не найдена по пути $BasePath" "WARN"
        Write-Host ""
        Write-Host "  Создать ИБ:" -ForegroundColor Yellow
        Write-Host "    1cv8.exe CREATEINFOBASE File=`"$BasePath`"" -ForegroundColor DarkGray
    }

    if (Test-Path (Join-Path $ConfigPath "Configuration.xml")) {
        Write-Step "XML" "Configuration.xml найден в исходниках" "OK"
    } else {
        Write-Step "XML" "Configuration.xml не найден!" "FAIL"
    }
    Write-Host ""
}

function Step-Validate {
    Write-Step "1. ВАЛИДАЦИЯ" "Запуск validate-config.ps1..."
    $validateScript = Join-Path $scriptDir "validate-config.ps1"
    if (Test-Path $validateScript) {
        # Захват вывода валидатора
        $validateOutput = & powershell -ExecutionPolicy Bypass -File $validateScript 2>&1 | Out-String

        # Проверяем на наличие ошибок (русский и английский текст)
        $hasErrors = $validateOutput -match "\[ОШИБКА\]|\[FAIL\]|ОШИБОК\s*:\s*[1-9]"
        
        # Выводим результат валидатора ВСЕГДА (чтобы агент видел)
        Write-Host $validateOutput

        if ($hasErrors) {
            Write-Step "1. ВАЛИДАЦИЯ" "Найдены ошибки XML-структуры" "FAIL"
            Write-Host ""
            Write-Host "================================================================" -ForegroundColor Red
            Write-Host "=== ОШИБКИ ВАЛИДАЦИИ (для Copilot Agent) ===" -ForegroundColor Red
            Write-Host "================================================================" -ForegroundColor Red
            Write-Host ""
            Write-Host "  Агент ОБЯЗАН исправить ВСЕ строки [ОШИБКА] из вывода выше," -ForegroundColor Cyan
            Write-Host "  затем запустить deploy-config.ps1 -Action Full повторно." -ForegroundColor Cyan
            Write-Host ""
            Write-Host "================================================================" -ForegroundColor Red
            Write-Host "=== КОНЕЦ ОШИБОК ВАЛИДАЦИИ ===" -ForegroundColor Red
            Write-Host "================================================================" -ForegroundColor Red
            return $false
        } else {
            Write-Step "1. ВАЛИДАЦИЯ" "XML-структура корректна" "OK"
            return $true
        }
    } else {
        Write-Step "1. ВАЛИДАЦИЯ" "validate-config.ps1 не найден, пропускаем" "WARN"
        return $true
    }
}

function Step-Load {
    Write-Step "2. ЗАГРУЗКА" "Загрузка конфигурации из XML-файлов..."
    $result = Invoke-1C -Mode "DESIGNER" -ExtraArgs @("/LoadConfigFromFiles", "`"$ConfigPath`"")

    $parseResult = Parse-1CErrors -LogContent $result.Log -Stdout $result.Stdout -Stderr $result.Stderr -OperationFailed ($result.ExitCode -ne 0)

    if ($result.ExitCode -eq 0 -and $parseResult.Errors.Count -eq 0) {
        Write-Step "2. ЗАГРУЗКА" "Конфигурация загружена успешно" "OK"
        return @{ Success = $true; Errors = @(); Warnings = $parseResult.Warnings }
    } elseif ($result.ExitCode -eq 0 -and $parseResult.Errors.Count -gt 0) {
        # Успех по коду, но нашлись ошибки в выводе — считаем предупреждениями
        Write-Step "2. ЗАГРУЗКА" "Загружена, но есть предупреждения ($($parseResult.Errors.Count))" "WARN"
        $parseResult.Errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        return @{ Success = $true; Errors = @(); Warnings = $parseResult.Errors }
    } else {
        # Реальная ошибка
        Write-Step "2. ЗАГРУЗКА" "ОШИБКА загрузки (exit code: $($result.ExitCode))" "FAIL"
        Format-ErrorBlockForAgent `
            -Stage "ЗАГРУЗКА (LoadConfigFromFiles)" `
            -ExitCode $result.ExitCode `
            -Errors $parseResult.Errors `
            -Warnings $parseResult.Warnings `
            -RawLog $result.Log `
            -LogFile $result.LogFile `
            -Stdout $result.Stdout `
            -Stderr $result.Stderr `
            -TimedOut $result.TimedOut
        return @{ Success = $false; Errors = $parseResult.Errors; Log = $result.Log; LogFile = $result.LogFile }
    }
}

function Step-Check {
    Write-Step "3. ПРОВЕРКА" "Синтакс-контроль конфигурации..."
    $result = Invoke-1C -Mode "DESIGNER" -ExtraArgs @(
        "/CheckConfig",
        "-Server",
        "-ThinClient",
        "-WebClient",
        "-ExternalConnection",
        "-ThickClientOrdinaryApplication",
        "-ExtendedModulesCheck"
    )

    $parseResult = Parse-1CErrors -LogContent $result.Log -Stdout $result.Stdout -Stderr $result.Stderr -OperationFailed ($result.ExitCode -ne 0)

    if ($result.ExitCode -eq 0 -and $parseResult.Errors.Count -eq 0) {
        Write-Step "3. ПРОВЕРКА" "Синтакс-контроль пройден успешно" "OK"
        return @{ Success = $true; Errors = @() }
    } else {
        Write-Step "3. ПРОВЕРКА" "Найдено ошибок: $($parseResult.Errors.Count)" "FAIL"
        Format-ErrorBlockForAgent `
            -Stage "СИНТАКС-КОНТРОЛЬ (CheckConfig)" `
            -ExitCode $result.ExitCode `
            -Errors $parseResult.Errors `
            -Warnings $parseResult.Warnings `
            -RawLog $result.Log `
            -LogFile $result.LogFile `
            -Stdout $result.Stdout `
            -Stderr $result.Stderr `
            -TimedOut $result.TimedOut
        return @{ Success = $false; Errors = $parseResult.Errors; Log = $result.Log; LogFile = $result.LogFile }
    }
}

function Step-Update {
    Write-Step "4. ОБНОВЛЕНИЕ БД" "Обновление конфигурации базы данных..."
    $result = Invoke-1C -Mode "DESIGNER" -ExtraArgs @("/UpdateDBCfg")

    $parseResult = Parse-1CErrors -LogContent $result.Log -Stdout $result.Stdout -Stderr $result.Stderr -OperationFailed ($result.ExitCode -ne 0)

    if ($result.ExitCode -eq 0) {
        Write-Step "4. ОБНОВЛЕНИЕ БД" "Конфигурация БД обновлена" "OK"
        return @{ Success = $true; Errors = @() }
    } else {
        Write-Step "4. ОБНОВЛЕНИЕ БД" "ОШИБКА обновления БД" "FAIL"
        Format-ErrorBlockForAgent `
            -Stage "ОБНОВЛЕНИЕ_БД (UpdateDBCfg)" `
            -ExitCode $result.ExitCode `
            -Errors $parseResult.Errors `
            -Warnings $parseResult.Warnings `
            -RawLog $result.Log `
            -LogFile $result.LogFile `
            -Stdout $result.Stdout `
            -Stderr $result.Stderr `
            -TimedOut $result.TimedOut
        return @{ Success = $false; Errors = $parseResult.Errors; Log = $result.Log }
    }
}

function Step-Run {
    Write-Step "5. ЗАПУСК" "Запуск 1С:Предприятие..."
    $allArgs = @("ENTERPRISE", "/F", "`"$BasePath`"")
    if ($User) { $allArgs += @("/N", "`"$User`"") }
    if ($Password) { $allArgs += @("/P", "`"$Password`"") }
    $allArgs += "/DisableStartupDialogs"

    $argString = $allArgs -join " "
    Start-Process -FilePath $v8exe -ArgumentList $argString
    Write-Step "5. ЗАПУСК" "1С:Предприятие запущено" "OK"
}

function Step-OpenDesigner {
    Write-Step "КОНФИГУРАТОР" "Открытие конфигуратора..."
    $allArgs = @("DESIGNER", "/F", "`"$BasePath`"")
    if ($User) { $allArgs += @("/N", "`"$User`"") }
    if ($Password) { $allArgs += @("/P", "`"$Password`"") }

    $argString = $allArgs -join " "
    Start-Process -FilePath $v8exe -ArgumentList $argString
    Write-Step "КОНФИГУРАТОР" "Конфигуратор открыт" "OK"
}

# === MAIN ===

Write-Host ""
Write-Host "========== PTM Deploy: $Action ==========" -ForegroundColor Cyan
Write-Host "========== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==========" -ForegroundColor DarkGray
Write-Host ""

switch ($Action) {
    "Info" {
        Show-Info
    }
    "Load" {
        $r = Step-Load
        if (-not $r.Success) { exit 1 }
    }
    "Check" {
        $r = Step-Check
        if (-not $r.Success) { exit 1 }
    }
    "Update" {
        $r = Step-Update
        if (-not $r.Success) { exit 1 }
    }
    "Run" {
        Step-Run
    }
    "Designer" {
        Step-OpenDesigner
    }
    "Full" {
        $startTime = Get-Date

        # Шаг 1: Валидация XML
        $valid = Step-Validate
        if (-not $valid) {
            Write-Host ""
            Write-Step "ИТОГ" "Исправьте ошибки XML-валидации и повторите deploy-config.ps1 -Action Full" "FAIL"
            exit 1
        }

        # Шаг 2: Загрузка
        $loadResult = Step-Load
        if (-not $loadResult.Success) {
            Write-Host ""
            Write-Step "ИТОГ" "Загрузка ПРОВАЛЕНА. Агент ОБЯЗАН исправить ошибки и повторить деплой." "FAIL"
            exit 2
        }

        # Шаг 3: Синтакс-контроль
        $checkResult = Step-Check
        if (-not $checkResult.Success) {
            Write-Host ""
            Write-Step "ИТОГ" "Синтакс-контроль ПРОВАЛЕН. Агент ОБЯЗАН исправить BSL-код и повторить деплой." "FAIL"
            exit 3
        }

        # Шаг 4: Обновление БД
        $updateResult = Step-Update
        if (-not $updateResult.Success) {
            Write-Host ""
            Write-Step "ИТОГ" "Обновление БД ПРОВАЛЕНО. Агент ОБЯЗАН проанализировать лог и повторить деплой." "FAIL"
            exit 4
        }

        # Шаг 5: Открываем конфигуратор
        Step-OpenDesigner

        $elapsed = (Get-Date) - $startTime
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Step "ИТОГ" "Полный цикл завершён УСПЕШНО за $([math]::Round($elapsed.TotalSeconds)) сек. Конфигуратор открыт." "OK"
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
    }
}
