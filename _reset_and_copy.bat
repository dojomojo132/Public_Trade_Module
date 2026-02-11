@echo off
REM Удаление старой папки Проверка и копирование основной конфигурации
setlocal enabledelayedexpansion

echo Удаление старой папки Проверка...
if exist "D:\Git\Public_Trade_Module\Конфигурация\Проверка" (
    rmdir /S /Q "D:\Git\Public_Trade_Module\Конфигурация\Проверка"
    echo  ✓ Папка Проверка удалена
) else (
    echo  - Папка Проверка не существует
)

echo.
echo Копирование основной конфигурации...
xcopy "D:\Git\Public_Trade_Module\Конфигурация" "D:\Git\Public_Trade_Module\Конфигурация\Проверка" /E /I /Y >nul
echo  ✓ Конфигурация скопирована

echo.
echo Копирование завершено!
pause
