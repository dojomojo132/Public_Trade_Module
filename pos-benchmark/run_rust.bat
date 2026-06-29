@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
"D:\Git\Public_Trade_Module\pos-benchmark\rust-backend\target\release\pos-backend.exe"
