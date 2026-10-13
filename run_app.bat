@echo off
echo =========================================================
echo  Starting LinkedIn B2B Growth & Sales Copilot
echo =========================================================
echo.
echo Checking database and launching server at http://127.0.0.1:8080 ...
start http://127.0.0.1:8080
py -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8080 --reload
pause
