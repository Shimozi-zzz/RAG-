@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =============================================
echo    RAG 知识库问答系统 - 一键启动
echo =============================================
echo.

:: ==========================================
:: 1. 检测虚拟环境，不存在则自动创建
:: ==========================================
if not exist ".venv\\Scripts\\python.exe" (
    echo [1/3] 未检测到虚拟环境，正在创建 .venv ...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [错误] 创建虚拟环境失败，请检查是否已安装 Python 3.10+
        pause
        exit /b 1
    )
    echo [1/3] 虚拟环境创建成功
) else (
    echo [1/3] 检测到已存在的虚拟环境，跳过创建
)

:: ==========================================
:: 2. 激活虚拟环境
:: ==========================================
call ".venv\\Scripts\\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)

:: ==========================================
:: 3. 安装 / 更新依赖
:: ==========================================
echo.
echo [2/3] 检查并安装依赖（清华源 + 仅二进制包，跳过编译）...

:: 升级 pip 并使用清华源
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet

:: 安装依赖：--only-binary :all: 强制使用预编译包，避免 C++ 编译问题
pip install --only-binary :all: -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if %ERRORLEVEL% neq 0 (
    echo.
    echo [警告] 部分包安装失败，尝试宽松安装（允许源码编译）...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %ERRORLEVEL% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

:: ==========================================
:: 4. 启动服务
:: ==========================================
echo.
echo [3/3] 依赖就绪，启动服务 ...
echo.
echo   访问地址: http://localhost:8888/docs
echo   按 Ctrl+C 停止服务
echo =============================================
echo.

set PORT=8888
python -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload

if %ERRORLEVEL% neq 0 (
    echo.
    echo [提示] 端口 %PORT% 可能被占用，尝试端口 9999 ...
    set PORT=9999
    python -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload
)

pause