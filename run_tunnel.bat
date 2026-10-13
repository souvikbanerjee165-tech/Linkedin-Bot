@echo off
echo =========================================================
echo  Starting Cloudflare Public Tunnel for Port 8080
echo =========================================================
echo.
npx --yes cloudflared tunnel --url http://127.0.0.1:8080
pause
