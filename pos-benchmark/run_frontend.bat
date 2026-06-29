@echo off
cd /d "D:\Git\Public_Trade_Module\pos-benchmark\frontend"
start "" http://localhost:8080
python -m http.server 8080
