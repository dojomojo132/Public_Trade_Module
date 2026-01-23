@echo off
chcp 65001 >nul
title PTM Scanner Emulator - Quick Start
color 0B

echo.
echo ╔═══════════════════════════════════════════╗
echo ║   PTM Scanner Emulator - Quick Start     ║
echo ╚═══════════════════════════════════════════╝
echo.

:MENU
echo Выберите режим:
echo.
echo [1] PowerShell - Простой (без установки)
echo [2] Electron GUI - С интерфейсом (требует npm install)
echo [3] Тестовое сканирование (4820000123456)
echo [4] Выход
echo.
set /p choice="Ваш выбор: "

if "%choice%"=="1" goto PS
if "%choice%"=="2" goto ELECTRON
if "%choice%"=="3" goto TEST
if "%choice%"=="4" goto END

echo Неверный выбор!
goto MENU

:PS
echo.
echo Запуск PowerShell эмулятора...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ScanSimple.ps1"
goto END

:ELECTRON
echo.
echo Проверка Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Node.js не установлен!
    echo Скачайте: https://nodejs.org/
    pause
    goto MENU
)

if not exist "%~dp0node_modules" (
    echo.
    echo Первый запуск - установка зависимостей...
    echo Это займёт 2-3 минуты...
    cd /d "%~dp0"
    call npm install
    if errorlevel 1 (
        echo ОШИБКА установки!
        pause
        goto MENU
    )
)

echo.
echo Запуск Electron GUI...
cd /d "%~dp0"
call npm start
goto END

:TEST
echo.
echo Тестовое сканирование через 3 секунды...
echo ПЕРЕКЛЮЧИТЕСЬ НА ОКНО 1С!
timeout /t 3 /nobreak >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ScanSimple.ps1" -Barcode "4820000123456"
echo.
pause
goto MENU

:END
exit
