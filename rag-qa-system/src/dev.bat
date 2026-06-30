@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =============================================
echo    RAG QA System - Development Mode
echo =============================================
echo.
echo    URL:  http://localhost:8000/docs
echo    Stop: Press Ctrl+C
echo.

REM 使用系统已安装的 Python 运行（开发环境）
python -m uvicorn app.main:app --host 127.0.0.1 --port 3000 --reload

pause