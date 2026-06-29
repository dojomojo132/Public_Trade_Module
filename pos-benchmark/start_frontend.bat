@echo off
cd /d "D:\Git\Public_Trade_Module\pos-benchmark\frontend"
start "" http://localhost:8080/rust.html
start "" http://localhost:8080/go.html
python -m http.server 8080
