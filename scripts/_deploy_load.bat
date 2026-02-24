@echo off
powershell -ExecutionPolicy Bypass -File "D:\Git\Public_Trade_Module\Документация\Валидация\deploy-config.ps1" -Action Load -User "Админ" >"D:\Git\Public_Trade_Module\logs\_deploy_load_test.txt" 2>&1
echo EXIT=%ERRORLEVEL%
