@echo off
chcp 65001 >nul
setlocal

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║      1C Copilot Agent Framework — Первый запуск         ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Шаг 1: Проверка Python ────────────────────────────────────────────────────
echo [1/5] Проверка Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден. Установите Python 3.10+ с https://python.org
    pause
    exit /b 1
)

:: ── Шаг 2: Проверка Node.js ───────────────────────────────────────────────────
echo [2/5] Проверка Node.js...
node --version 2>nul
if %errorlevel% neq 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: Node.js не найден. JavaScript-утилиты не будут работать.
    echo   Установите с https://nodejs.org (опционально)
    echo.
) else (
    echo [3/5] Установка Node.js зависимостей...
    npm install
    if %errorlevel% neq 0 (
        echo ПРЕДУПРЕЖДЕНИЕ: npm install завершился с ошибкой.
    )
)

:: ── Шаг 4: Создание Python venv ───────────────────────────────────────────────
echo [4/5] Создание Python виртуального окружения (.venv)...
if not exist ".venv" (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ОШИБКА: не удалось создать venv
        pause
        exit /b 1
    )
    echo   .venv создан
) else (
    echo   .venv уже существует, пропускаю
)

:: ── Шаг 5: Установка Python зависимостей ─────────────────────────────────────
echo [5/5] Установка Python зависимостей...
.venv\Scripts\pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: pip install завершился с ошибкой.
    echo   Проверь requirements.txt и попробуй вручную:
    echo   .venv\Scripts\pip install -r requirements.txt
)

:: ── Готово ────────────────────────────────────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                   Установка завершена!                   ║
echo  ╠══════════════════════════════════════════════════════════╣
echo  ║  Следующие шаги:                                         ║
echo  ║                                                          ║
echo  ║  1. Открой .github\project-config.yml                   ║
echo  ║     Заполни: project.name, paths.infobase                ║
echo  ║                                                          ║
echo  ║  2. Открой .vscode\mcp.json                             ║
echo  ║     Раскомментируй нужные MCP-серверы                    ║
echo  ║                                                          ║
echo  ║  3. Запусти выгрузку конфигурации:                       ║
echo  ║     python scripts\_ps_wrapper.py deploy -Action Dump    ║
echo  ║                                                          ║
echo  ║  4. Открой VS Code в этой папке:                         ║
echo  ║     code .                                               ║
echo  ║                                                          ║
echo  ║  5. В VS Code Chat напиши:                               ║
echo  ║     /1c-new-task Запустить настройку проекта             ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
pause
