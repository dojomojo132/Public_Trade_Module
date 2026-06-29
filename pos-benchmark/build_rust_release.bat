@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d "D:\Git\Public_Trade_Module\pos-benchmark\rust-backend"
cargo build --release 2>&1
