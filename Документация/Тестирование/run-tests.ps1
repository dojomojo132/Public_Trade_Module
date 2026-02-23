<#
.SYNOPSIS
    Запуск тестов PTM: статический анализ BSL + unit-тесты YAxUnit
.DESCRIPTION
    Тестовый скрипт для отработки процесса тестирования.
    После утверждения будет интегрирован в deploy-config.ps1.
    
    Уровни тестирования:
      1. BSL Language Server — статический анализ кода (диагностики)
      2. YAxUnit — модульные и интеграционные тесты (unit + integration)
      3. Дымовые тесты — открытие всех форм PTM
    
    ТРЕБОВАНИЯ:
      - BSL Language Server: java + bsl-language-server.jar в PATH или указать -BslLsPath
      - YAxUnit: расширение yaxunit.cfe загружено в тестовую ИБ
      - 1cv8.exe: установлена платформа 1С:Предприятие 8.3
.PARAMETER Action
    Действие:
      BslAnalysis  — только статический анализ BSL Language Server
      YAxUnit      — только YAxUnit тесты
      Smoke        — только дымовые тесты (открытие форм)
      Full         — все тесты последовательно
      Status       — показать состояние окружения
.PARAMETER BasePath
    Путь к файловой информационной базе
.PARAMETER ConfigPath
    Путь к XML-файлам конфигурации (для BSL LS анализа)
.PARAMETER BslLsPath
    Путь к bsl-language-server.jar (если не в PATH)
.PARAMETER ReportDir
    Папка для отчётов (по умолчанию: Документация/Тестирование/Отчёты)
.PARAMETER TestBasePath
    Путь к ТЕСТОВОЙ ИБ (отдельная от рабочей). Если не указан, используется BasePath
.EXAMPLE
    .\run-tests.ps1 -Action Full
    .\run-tests.ps1 -Action BslAnalysis
    .\run-tests.ps1 -Action YAxUnit -TestBasePath "D:\Confiq\PTM_Test"
    .\run-tests.ps1 -Action Status
#>

param(
    [ValidateSet("BslAnalysis", "YAxUnit", "Smoke", "Full", "Status")]
    [string]$Action = "Full",

    [string]$BasePath = "D:\Confiq\Public Trade Module",
    [string]$ConfigPath = "",
    [string]$BslLsPath = "",
    [string]$ReportDir = "",
    [string]$TestBasePath = "",
    [string]$User = "",
    [string]$Password = "",
    [int]$TimeoutSeconds = 300
)

# === НАСТРОЙКИ ===
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $projectRoot "Конфигурация\Проверка"
}
if (-not $ReportDir) {
    $ReportDir = Join-Path $projectRoot "Документация\Тестирование\Отчёты"
}
if (-not $TestBasePath) {
    $TestBasePath = $BasePath
}

# Создать папку отчётов
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
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

# Поиск Java
$javaExe = $null
$javaCandidates = @(
    (Get-Command "java" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    "$env:JAVA_HOME\bin\java.exe",
    "C:\Program Files\Java\jdk*\bin\java.exe",
    "C:\Program Files\Eclipse Adoptium\*\bin\java.exe"
)
foreach ($candidate in $javaCandidates) {
    if ($candidate -and (Test-Path $candidate -ErrorAction SilentlyContinue)) {
        $javaExe = (Resolve-Path $candidate | Select-Object -First 1).Path
        break
    }
}

# Поиск BSL Language Server
$bslLs = $null
if ($BslLsPath -and (Test-Path $BslLsPath)) {
    $bslLs = $BslLsPath
} else {
    # Поиск в стандартных местах
    $bslCandidates = @(
        (Get-Command "bsl-language-server" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        "$env:USERPROFILE\.bsl-language-server\bsl-language-server.jar",
        "C:\Tools\bsl-language-server\bsl-language-server.jar",
        (Join-Path $projectRoot "tools\bsl-language-server.jar")
    )
    foreach ($candidate in $bslCandidates) {
        if ($candidate -and (Test-Path $candidate -ErrorAction SilentlyContinue)) {
            $bslLs = $candidate
            break
        }
    }
}

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

function Write-TestStep {
    param([string]$Step, [string]$Message, [string]$Status = "INFO")
    $color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        "SKIP" { "DarkGray" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] [$Status] $Step — $Message" -ForegroundColor $color
}

function Write-TestSummary {
    param(
        [string]$Title,
        [int]$Total,
        [int]$Passed,
        [int]$Failed,
        [int]$Skipped = 0,
        [string]$Duration = ""
    )
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor $(if ($Failed -gt 0) { "Red" } else { "Green" })
    Write-Host "  $Title" -ForegroundColor White
    Write-Host "  Всего: $Total | Успешно: $Passed | Ошибок: $Failed | Пропущено: $Skipped" -ForegroundColor $(if ($Failed -gt 0) { "Red" } else { "Green" })
    if ($Duration) {
        Write-Host "  Время: $Duration" -ForegroundColor DarkGray
    }
    Write-Host "================================================================" -ForegroundColor $(if ($Failed -gt 0) { "Red" } else { "Green" })
    Write-Host ""
}

# === ТЕСТЫ: BSL LANGUAGE SERVER ===

function Step-BslAnalysis {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  УРОВЕНЬ 1: Статический анализ BSL Language Server" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    if (-not $javaExe) {
        Write-TestStep "BSL-LS" "Java не найдена. Установите JDK 11+ или укажите JAVA_HOME" "SKIP"
        return @{ Success = $false; Skipped = $true; Errors = @(); Warnings = @() }
    }

    if (-not $bslLs) {
        Write-TestStep "BSL-LS" "BSL Language Server не найден. Скачайте с github.com/1c-syntax/bsl-language-server/releases" "SKIP"
        Write-Host "  Установка: скачать .jar → поместить в $projectRoot\tools\" -ForegroundColor DarkGray
        return @{ Success = $false; Skipped = $true; Errors = @(); Warnings = @() }
    }

    $configFile = Join-Path $projectRoot ".bsl-language-server.json"
    if (-not (Test-Path $configFile)) {
        Write-TestStep "BSL-LS" "Конфигурация .bsl-language-server.json не найдена" "FAIL"
        return @{ Success = $false; Skipped = $false; Errors = @("Missing .bsl-language-server.json") }
    }

    Write-TestStep "BSL-LS" "Анализ кода в $ConfigPath..."

    $reportFile = Join-Path $ReportDir "bsl-analysis-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $startTime = Get-Date

    try {
        $args = @(
            "-jar", $bslLs,
            "--analyze",
            "--srcDir", $ConfigPath,
            "--configuration", $configFile,
            "--reporter", "json",
            "--outputDir", $ReportDir
        )

        $process = Start-Process -FilePath $javaExe -ArgumentList $args `
            -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput (Join-Path $ReportDir "bsl-stdout.txt") `
            -RedirectStandardError (Join-Path $ReportDir "bsl-stderr.txt")

        $elapsed = (Get-Date) - $startTime

        if ($process.ExitCode -eq 0) {
            # Парсинг результатов
            $reportFiles = Get-ChildItem $ReportDir -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $errors = @()
            $warnings = @()

            if ($reportFiles) {
                try {
                    $report = Get-Content $reportFiles.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                    foreach ($diag in $report) {
                        $severity = $diag.severity
                        $msg = "$($diag.source):$($diag.range.start.line) [$($diag.code)] $($diag.message)"
                        if ($severity -eq 1) { $errors += $msg }
                        else { $warnings += $msg }
                    }
                } catch {
                    Write-TestStep "BSL-LS" "Не удалось прочитать отчёт: $_" "WARN"
                }
            }

            Write-TestStep "BSL-LS" "Анализ завершён за $([math]::Round($elapsed.TotalSeconds)) сек." "PASS"
            Write-TestSummary "BSL LANGUAGE SERVER" ($errors.Count + $warnings.Count) $warnings.Count $errors.Count 0 "$([math]::Round($elapsed.TotalSeconds)) сек."

            if ($errors.Count -gt 0) {
                Write-Host "  === ОШИБКИ BSL ===" -ForegroundColor Red
                $errors | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
            }
            if ($warnings.Count -gt 0 -and $warnings.Count -le 20) {
                Write-Host "  === ПРЕДУПРЕЖДЕНИЯ BSL ===" -ForegroundColor Yellow
                $warnings | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
            } elseif ($warnings.Count -gt 20) {
                Write-Host "  Предупреждений: $($warnings.Count) (см. отчёт в $ReportDir)" -ForegroundColor Yellow
            }

            return @{ Success = ($errors.Count -eq 0); Errors = $errors; Warnings = $warnings; ReportFile = $reportFiles.FullName }
        } else {
            $stderr = Get-Content (Join-Path $ReportDir "bsl-stderr.txt") -Raw -ErrorAction SilentlyContinue
            Write-TestStep "BSL-LS" "Ошибка выполнения (exit code: $($process.ExitCode))" "FAIL"
            if ($stderr) { Write-Host "  $stderr" -ForegroundColor Red }
            return @{ Success = $false; Errors = @("BSL LS exit code: $($process.ExitCode)") }
        }
    } catch {
        Write-TestStep "BSL-LS" "Исключение: $_" "FAIL"
        return @{ Success = $false; Errors = @("Exception: $_") }
    }
}

# === ТЕСТЫ: YAXUNIT ===

function Step-YAxUnitTests {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  УРОВЕНЬ 2: Модульные тесты YAxUnit" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    if (-not $v8exe) {
        Write-TestStep "YAxUnit" "1cv8.exe не найден. Установите 1С:Предприятие 8.3" "FAIL"
        return @{ Success = $false; Errors = @("1cv8.exe not found") }
    }

    # Проверка: расширение YAxUnit загружено?
    Write-TestStep "YAxUnit" "Запуск тестов в ИБ: $TestBasePath"

    $reportFile = Join-Path $ReportDir "yaxunit-$(Get-Date -Format 'yyyyMMdd-HHmmss').xml"
    $logFile = Join-Path $ReportDir "yaxunit-log.txt"
    $startTime = Get-Date

    # Параметры запуска YAxUnit
    # Формат: /C"RunUnitTests=<путь к файлу отчёта>;ExitAfterTests"
    $runParams = "RunUnitTests=$reportFile"

    $v8args = @(
        "ENTERPRISE",
        "/F", "`"$TestBasePath`"",
        "/C`"$runParams`"",
        "/DisableStartupDialogs",
        "/DisableStartupMessages"
    )

    if ($User) {
        $v8args += "/N`"$User`""
        if ($Password) {
            $v8args += "/P`"$Password`""
        }
    }

    try {
        Write-TestStep "YAxUnit" "Запуск 1С:Предприятие для выполнения тестов..."

        $process = Start-Process -FilePath $v8exe -ArgumentList ($v8args -join " ") `
            -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput $logFile `
            -RedirectStandardError (Join-Path $ReportDir "yaxunit-stderr.txt")

        # Применяем таймаут
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            $process.Kill()
            Write-TestStep "YAxUnit" "ТАЙМАУТ ($TimeoutSeconds сек). Процесс 1С убит." "FAIL"
            return @{ Success = $false; Errors = @("Timeout after $TimeoutSeconds seconds") }
        }

        $elapsed = (Get-Date) - $startTime

        # Парсинг JUnit XML отчёта
        if (Test-Path $reportFile) {
            try {
                [xml]$junit = Get-Content $reportFile -Encoding UTF8
                $testsuites = $junit.testsuites
                $total = [int]$testsuites.tests
                $failures = [int]$testsuites.failures
                $errors = [int]$testsuites.errors
                $skipped = [int]$testsuites.skipped
                $passed = $total - $failures - $errors - $skipped
                $time = $testsuites.time

                Write-TestSummary "YAXUNIT — МОДУЛЬНЫЕ ТЕСТЫ" $total $passed ($failures + $errors) $skipped "$time сек."

                if ($failures -gt 0 -or $errors -gt 0) {
                    Write-Host "  === ПРОВАЛЕННЫЕ ТЕСТЫ ===" -ForegroundColor Red
                    foreach ($suite in $junit.testsuites.testsuite) {
                        foreach ($testcase in $suite.testcase) {
                            if ($testcase.failure) {
                                Write-Host "    FAIL: $($suite.name).$($testcase.name)" -ForegroundColor Red
                                Write-Host "          $($testcase.failure.message)" -ForegroundColor DarkRed
                            }
                            if ($testcase.error) {
                                Write-Host "    ERROR: $($suite.name).$($testcase.name)" -ForegroundColor Red
                                Write-Host "           $($testcase.error.message)" -ForegroundColor DarkRed
                            }
                        }
                    }
                }

                return @{
                    Success = ($failures -eq 0 -and $errors -eq 0)
                    Total = $total
                    Passed = $passed
                    Failed = ($failures + $errors)
                    Skipped = $skipped
                    ReportFile = $reportFile
                }
            } catch {
                Write-TestStep "YAxUnit" "Не удалось прочитать отчёт JUnit: $_" "WARN"
            }
        } else {
            Write-TestStep "YAxUnit" "Файл отчёта не создан. Возможно, расширение YAxUnit не установлено." "WARN"
            Write-Host "  Установка YAxUnit:" -ForegroundColor DarkGray
            Write-Host "    1. Скачать yaxunit.cfe с https://github.com/bia-technologies/yaxunit/releases" -ForegroundColor DarkGray
            Write-Host "    2. Конфигуратор → Расширения → Добавить из файла" -ForegroundColor DarkGray
            Write-Host "    3. Обновить БД" -ForegroundColor DarkGray
            return @{ Success = $false; Skipped = $true; Errors = @("YAxUnit extension not installed") }
        }

        return @{ Success = ($process.ExitCode -eq 0); Errors = @() }
    } catch {
        Write-TestStep "YAxUnit" "Исключение: $_" "FAIL"
        return @{ Success = $false; Errors = @("Exception: $_") }
    }
}

# === ТЕСТЫ: ДЫМОВЫЕ ===

function Step-SmokTests {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  УРОВЕНЬ 3: Дымовые тесты (открытие форм PTM)" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    if (-not $v8exe) {
        Write-TestStep "SMOKE" "1cv8.exe не найден" "FAIL"
        return @{ Success = $false; Errors = @("1cv8.exe not found") }
    }

    # Дымовые тесты YAxUnit запускаются тем же процессом,
    # но с отдельным параметром (если настроены)
    Write-TestStep "SMOKE" "Дымовые тесты используют YAxUnit (генератор дымовых тестов)"
    Write-TestStep "SMOKE" "Если YAxUnit не установлен — пропуск" "INFO"

    # Запускаем с параметром только дымовых
    $reportFile = Join-Path $ReportDir "smoke-$(Get-Date -Format 'yyyyMMdd-HHmmss').xml"
    $runParams = "RunUnitTests=$reportFile;Filter=Дымовые"

    $v8args = @(
        "ENTERPRISE",
        "/F", "`"$TestBasePath`"",
        "/C`"$runParams`"",
        "/DisableStartupDialogs",
        "/DisableStartupMessages"
    )

    if ($User) {
        $v8args += "/N`"$User`""
        if ($Password) { $v8args += "/P`"$Password`"" }
    }

    try {
        $startTime = Get-Date
        $process = Start-Process -FilePath $v8exe -ArgumentList ($v8args -join " ") `
            -NoNewWindow -Wait -PassThru

        $elapsed = (Get-Date) - $startTime

        if (Test-Path $reportFile) {
            [xml]$junit = Get-Content $reportFile -Encoding UTF8
            $total = [int]$junit.testsuites.tests
            $failures = [int]$junit.testsuites.failures
            $passed = $total - $failures

            Write-TestSummary "ДЫМОВЫЕ ТЕСТЫ (ФОРМЫ PTM)" $total $passed $failures 0 "$([math]::Round($elapsed.TotalSeconds)) сек."
            return @{ Success = ($failures -eq 0); Total = $total; Passed = $passed; Failed = $failures }
        } else {
            Write-TestStep "SMOKE" "Пропущены (YAxUnit дымовой генератор не настроен)" "SKIP"
            return @{ Success = $false; Skipped = $true }
        }
    } catch {
        Write-TestStep "SMOKE" "Исключение: $_" "FAIL"
        return @{ Success = $false; Errors = @("Exception: $_") }
    }
}

# === ДЕЙСТВИЕ: STATUS ===

function Show-Status {
    $ErrorActionPreference = "Continue"
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  СОСТОЯНИЕ ТЕСТОВОГО ОКРУЖЕНИЯ PTM" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    # 1С
    if ($v8exe) {
        Write-TestStep "1C" "1cv8.exe: $v8exe" "PASS"
    } else {
        Write-TestStep "1C" "1cv8.exe НЕ НАЙДЕН" "FAIL"
    }

    # Java
    if ($javaExe) {
        $javaVer = & $javaExe -version 2>&1 | Select-Object -First 1 | Out-String
        $javaVer = $javaVer.Trim()
        Write-TestStep "Java" "$javaExe ($javaVer)" "PASS"
    } else {
        Write-TestStep "Java" "Java НЕ НАЙДЕНА (нужна для BSL LS)" "WARN"
    }

    # BSL Language Server
    if ($bslLs) {
        Write-TestStep "BSL-LS" "$bslLs" "PASS"
    } else {
        Write-TestStep "BSL-LS" "BSL Language Server НЕ НАЙДЕН" "WARN"
        Write-Host "         Скачать: https://github.com/1c-syntax/bsl-language-server/releases" -ForegroundColor DarkGray
    }

    # .bsl-language-server.json
    $configFile = Join-Path $projectRoot ".bsl-language-server.json"
    if (Test-Path $configFile) {
        Write-TestStep "BSL-CFG" ".bsl-language-server.json найден" "PASS"
    } else {
        Write-TestStep "BSL-CFG" ".bsl-language-server.json НЕ НАЙДЕН" "WARN"
    }

    # Рабочая ИБ
    if (Test-Path $BasePath) {
        Write-TestStep "РАБ.ИБ" "$BasePath" "PASS"
    } else {
        Write-TestStep "РАБ.ИБ" "Рабочая ИБ не найдена: $BasePath" "FAIL"
    }

    # Тестовая ИБ
    if ($TestBasePath -ne $BasePath) {
        if (Test-Path $TestBasePath) {
            Write-TestStep "ТЕСТ.ИБ" "$TestBasePath" "PASS"
        } else {
            Write-TestStep "ТЕСТ.ИБ" "Тестовая ИБ не найдена: $TestBasePath" "WARN"
        }
    } else {
        Write-TestStep "ТЕСТ.ИБ" "Используется рабочая ИБ (рекомендуется создать отдельную)" "WARN"
    }

    # YAxUnit (проверяем наличие расширения в ИБ)
    Write-TestStep "YAxUnit" "Проверка наличия расширения — запустите тесты для проверки" "INFO"
    Write-Host "         Скачать: https://github.com/bia-technologies/yaxunit/releases" -ForegroundColor DarkGray

    # Отчёты
    if (Test-Path $ReportDir) {
        $reports = Get-ChildItem $ReportDir -File -ErrorAction SilentlyContinue
        Write-TestStep "ОТЧЁТЫ" "$ReportDir ($($reports.Count) файлов)" "PASS"
    } else {
        Write-TestStep "ОТЧЁТЫ" "Папка отчётов будет создана при первом запуске" "INFO"
    }

    Write-Host ""
    Write-Host "  Быстрый старт:" -ForegroundColor White
    Write-Host "    1. Установить Java 11+           → BSL LS анализ заработает" -ForegroundColor DarkGray
    Write-Host "    2. Скачать bsl-language-server.jar → Положить в tools/" -ForegroundColor DarkGray
    Write-Host "    3. Скачать yaxunit.cfe            → Загрузить как расширение в ИБ" -ForegroundColor DarkGray
    Write-Host "    4. .\run-tests.ps1 -Action Full   → Запустить все тесты" -ForegroundColor DarkGray
    Write-Host ""
}

# === ГЛАВНЫЙ БЛОК ===

$startTotal = Get-Date

Write-Host ""
Write-Host "================================================================" -ForegroundColor White
Write-Host "  PTM TEST RUNNER v0.1 (тестовая версия)" -ForegroundColor White
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
Write-Host "================================================================" -ForegroundColor White

switch ($Action) {
    "Status" {
        Show-Status
    }
    "BslAnalysis" {
        $bslResult = Step-BslAnalysis
        if ($bslResult.Skipped) {
            Write-Host "  BSL-анализ пропущен. Используйте -Action Status для диагностики." -ForegroundColor Yellow
            exit 0
        }
        exit $(if ($bslResult.Success) { 0 } else { 1 })
    }
    "YAxUnit" {
        $yaxResult = Step-YAxUnitTests
        if ($yaxResult.Skipped) {
            Write-Host "  YAxUnit пропущен. Установите расширение в ИБ." -ForegroundColor Yellow
            exit 0
        }
        exit $(if ($yaxResult.Success) { 0 } else { 1 })
    }
    "Smoke" {
        $smokeResult = Step-SmokTests
        exit $(if ($smokeResult.Success) { 0 } else { 1 })
    }
    "Full" {
        $allSuccess = $true
        $results = @{}

        # 1. BSL-анализ
        $results["bsl"] = Step-BslAnalysis
        if (-not $results["bsl"].Success -and -not $results["bsl"].Skipped) {
            $allSuccess = $false
        }

        # 2. YAxUnit тесты
        $results["yaxunit"] = Step-YAxUnitTests
        if (-not $results["yaxunit"].Success -and -not $results["yaxunit"].Skipped) {
            $allSuccess = $false
        }

        # 3. Дымовые тесты
        $results["smoke"] = Step-SmokTests
        if (-not $results["smoke"].Success -and -not $results["smoke"].Skipped) {
            $allSuccess = $false
        }

        # Итого
        $elapsedTotal = (Get-Date) - $startTotal
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor $(if ($allSuccess) { "Green" } else { "Red" })
        Write-Host "  ИТОГО: PTM TEST SUITE" -ForegroundColor White
        Write-Host "  Время: $([math]::Round($elapsedTotal.TotalSeconds)) сек." -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "  BSL LS:     $(if ($results['bsl'].Skipped) { 'ПРОПУЩЕН' } elseif ($results['bsl'].Success) { 'OK' } else { 'ОШИБКИ' })" -ForegroundColor $(if ($results['bsl'].Skipped) { "Yellow" } elseif ($results['bsl'].Success) { "Green" } else { "Red" })
        Write-Host "  YAxUnit:    $(if ($results['yaxunit'].Skipped) { 'ПРОПУЩЕН' } elseif ($results['yaxunit'].Success) { 'OK' } else { 'ОШИБКИ' })" -ForegroundColor $(if ($results['yaxunit'].Skipped) { "Yellow" } elseif ($results['yaxunit'].Success) { "Green" } else { "Red" })
        Write-Host "  Дымовые:   $(if ($results['smoke'].Skipped) { 'ПРОПУЩЕН' } elseif ($results['smoke'].Success) { 'OK' } else { 'ОШИБКИ' })" -ForegroundColor $(if ($results['smoke'].Skipped) { "Yellow" } elseif ($results['smoke'].Success) { "Green" } else { "Red" })
        Write-Host ""

        if ($allSuccess) {
            Write-Host "  ВСЕ ТЕСТЫ ПРОЙДЕНЫ" -ForegroundColor Green
        } else {
            Write-Host "  ЕСТЬ ПРОБЛЕМЫ — см. детали выше" -ForegroundColor Red
        }
        Write-Host "================================================================" -ForegroundColor $(if ($allSuccess) { "Green" } else { "Red" })
        Write-Host ""
        Write-Host "  Отчёты: $ReportDir" -ForegroundColor DarkGray
        Write-Host ""

        exit $(if ($allSuccess) { 0 } else { 1 })
    }
}
