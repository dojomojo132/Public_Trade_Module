@echo off
set DEEPSEEK_API_KEY=sk-dd045b6a70e340c49ee2492e812ac4e0
cd /d D:\Git\Public_Trade_Module
"D:\Git\Public_Trade_Module\.graphify-venv\Scripts\python.exe" -m graphify.extract D:\Git\Public_Trade_Module --backend deepseek --model deepseek-v4-flash --max-concurrency 8 --token-budget 30000 > graphify-build.log 2>&1
echo DONE >> graphify-build.log
