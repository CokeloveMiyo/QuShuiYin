@echo off
title 清影 Qingying
echo [清影] 启动后端 :8051 ...
start "qingying-api" cmd /k "cd /d %~dp0backend && python app.py"
timeout /t 2 /nobreak >nul
echo [清影] 启动前端 :5173 ...
start "qingying-web" cmd /k "cd /d %~dp0frontend && npm run dev"
echo.
echo 打开浏览器访问 http://localhost:5173
pause
