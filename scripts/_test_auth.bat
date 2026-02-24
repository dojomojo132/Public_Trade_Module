@echo off
chcp 1251 > nul
"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe" DESIGNER /F "D:\Confiq\Public Trade Module" /U "Админ" /DumpIB "D:\Git\Public_Trade_Module\logs\_test_dump.dt" /DisableStartupDialogs /DisableStartupMessages /Out "D:\Git\Public_Trade_Module\logs\_test_auth.log"
echo EXIT_CODE=%ERRORLEVEL%
