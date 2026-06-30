# build_release.ps1 - RAG QA System 发布包打包脚本
# 使用方法: 在 rag-qa-system 根目录下运行 .\build_release.ps1

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $ScriptRoot "dist\rag-qa-system-release"
$EmbedDir = Join-Path $DistDir "python-embed"
$SrcDir = Join-Path $ScriptRoot "src"

$Mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
$PyVersion = "3.11.9"
$PyZipUrl = "https://www.python.org/ftp/python/$PyVersion/python-$PyVersion-embed-amd64.zip"
$GetPipUrl = "https://bootstrap.pypa.io/get-pip.py"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "   RAG QA System - Build Release Package" -ForegroundColor Cyan
Write-Host "   Python $PyVersion embeddable" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# =============================================
# Step 1: 清理 dist 目录
# =============================================
Write-Host "[Step 1/8] Cleaning dist directory ..." -ForegroundColor Yellow
if (Test-Path $DistDir) {
    Remove-Item -LiteralPath $DistDir -Recurse -Force
}
New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
New-Item -ItemType Directory -Path $EmbedDir -Force | Out-Null
Write-Host "  Done." -ForegroundColor Green

# =============================================
# Step 2: 下载 Python embeddable zip
# =============================================
Write-Host "[Step 2/8] Downloading Python $PyVersion embeddable ..." -ForegroundColor Yellow
$PyZipPath = Join-Path $DistDir "python-embed.zip"
Invoke-WebRequest -Uri $PyZipUrl -OutFile $PyZipPath -UseBasicParsing
$zipSize = [math]::Round((Get-Item $PyZipPath).Length / 1MB, 2)
Write-Host "  Downloaded $zipSize MB" -ForegroundColor Green

# =============================================
# Step 3: 解压并配置 python311._pth
# 【关键顺序】必须在安装 pip 之前修改 _pth 文件
# =============================================
Write-Host "[Step 3/8] Extracting and configuring Python embeddable ..." -ForegroundColor Yellow
Expand-Archive -LiteralPath $PyZipPath -DestinationPath $EmbedDir -Force
Remove-Item -LiteralPath $PyZipPath -Force

$PthPath = Join-Path $EmbedDir "python311._pth"
Set-Content -LiteralPath $PthPath -Value @(
    "python311.zip",
    ".",
    "Lib\site-packages",
    "import site"
) -Encoding ASCII

Write-Host "  python311._pth configured." -ForegroundColor Green
Write-Host "    -> Lib\site-packages added" -ForegroundColor DarkGray
Write-Host "    -> import site enabled" -ForegroundColor DarkGray

# =============================================
# Step 4: 安装 pip
# =============================================
Write-Host "[Step 4/8] Installing pip for embedded Python ..." -ForegroundColor Yellow
$GetPipPath = Join-Path $EmbedDir "get-pip.py"
Invoke-WebRequest -Uri $GetPipUrl -OutFile $GetPipPath -UseBasicParsing
$PythonExe = Join-Path $EmbedDir "python.exe"

& $PythonExe $GetPipPath --no-warn-script-location
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to install pip!" -ForegroundColor Red
    exit 1
}
Remove-Item -LiteralPath $GetPipPath -Force
Write-Host "  pip installed." -ForegroundColor Green

# =============================================
# Step 5: 安装项目依赖
# =============================================
Write-Host "[Step 5/8] Installing project dependencies ..." -ForegroundColor Yellow
Write-Host "  (This may take 5-15 minutes on first build)" -ForegroundColor DarkGray

$PipExe = Join-Path $EmbedDir "Scripts\pip.exe"

# 先升级 pip
& $PythonExe -m pip install --upgrade pip -i $Mirror --quiet 2>$null

# 【关键】先装 CPU 版 PyTorch，避免 sentence-transformers 拉入错误的 torch 版本
Write-Host "  [5a] Installing PyTorch (CPU-only) ..." -ForegroundColor DarkGray
& $PipExe install torch --index-url https://download.pytorch.org/whl/cpu -i $Mirror
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: PyTorch installation failed!" -ForegroundColor Red
    exit 1
}

# 再装其余依赖（torch 已满足，不会重复安装）
Write-Host "  [5b] Installing remaining dependencies ..." -ForegroundColor DarkGray
$RequirementsPath = Join-Path $SrcDir "requirements.txt"
& $PipExe install -r $RequirementsPath -i $Mirror
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Dependency installation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  All dependencies installed." -ForegroundColor Green

# =============================================
# Step 6: 验证关键包可正常 import
# =============================================
Write-Host "[Step 6/8] Verifying core packages import ..." -ForegroundColor Yellow
$checkScript = @'
import torch; print('  torch', torch.__version__)
import fastapi; print('  fastapi OK')
import langchain; print('  langchain OK')
import chromadb; print('  chromadb', chromadb.__version__)
import sentence_transformers; print('  sentence-transformers OK')
import huggingface_hub; print('  huggingface-hub OK')
'@

# 用临时文件传递多行脚本，避免 PowerShell 转义问题
$tmpPy = Join-Path $DistDir "_verify.py"
Set-Content -LiteralPath $tmpPy -Value $checkScript -Encoding UTF8
$verifyOut = & $PythonExe $tmpPy 2>&1
$exitCode = $LASTEXITCODE
Remove-Item -LiteralPath $tmpPy -Force

if ($exitCode -ne 0) {
    Write-Host "  ERROR: Verification failed!" -ForegroundColor Red
    Write-Host $verifyOut -ForegroundColor Red
    exit 1
}
Write-Host $verifyOut -ForegroundColor Green
Write-Host "  All packages verified." -ForegroundColor Green

# =============================================
# Step 7: 拷贝源代码到发布包
# =============================================
Write-Host "[Step 7/8] Copying source code ..." -ForegroundColor Yellow
$DistSrcDir = Join-Path $DistDir "src"

# robocopy: 排除 .env（防密钥泄露）、chroma_db/ uploads/（实例数据不进发布包）、__pycache__（字节码缓存）
robocopy $SrcDir $DistSrcDir /E /NP /NFL /NDL /XD "chroma_db" "uploads" "__pycache__" /XF ".env" 2>$null
if ($LASTEXITCODE -ge 8) {
    Write-Host "  ERROR: robocopy failed with code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# 确保 data 子目录存在（空目录，供新用户首次运行 Chroma 初始化）
$DistDataDir = Join-Path $DistSrcDir "data"
New-Item -ItemType Directory -Path (Join-Path $DistDataDir "chroma_db") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $DistDataDir "uploads") -Force | Out-Null

# 删除仅用于 Git 的空目录占位文件
Remove-Item -LiteralPath (Join-Path $DistDataDir "chroma_db\.gitkeep") -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $DistDataDir "uploads\.gitkeep") -Force -ErrorAction SilentlyContinue

Write-Host "  Source code copied (excluding .env, chroma_db/, uploads/)." -ForegroundColor Green

# =============================================
# Step 8: 生成 run.bat（UTF-8 with BOM）
# =============================================
Write-Host "[Step 8/8] Generating run.bat ..." -ForegroundColor Yellow
$RunBatPath = Join-Path $DistDir "run.bat"
$runBatContent = @'
@echo off
cd /d "%~dp0src"

set "PYTHON=..\python-embed\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] Portable Python not found: %~dp0python-embed\
    echo Do not move run.bat. Keep python-embed in the same folder.
    pause
    exit /b 1
)

if not exist ".env" (
    echo =============================================
    echo    RAG QA System - First Run Setup
    echo =============================================
    echo.
    echo .env file not found. Please do the following:
    echo   1. Rename .env.example to .env
    echo   2. Edit .env with Notepad, fill in your DEEPSEEK_API_KEY
    echo   3. Double-click run.bat again to start
    echo.
    echo Get API Key: https://platform.deepseek.com
    echo.
    pause
    exit /b 1
)

REM Extract PORT from .env, default 8888
for /f "tokens=2 delims==" %%a in ('findstr "^PORT=" .env 2^>nul') do set "PORT=%%a"
if "%PORT%"=="" set "PORT=8888"

echo =============================================
echo    RAG QA System - Portable Edition
echo =============================================
echo.
echo    URL:  http://localhost:%PORT%/docs
echo    Stop: Press Ctrl+C
echo.

"%PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port %PORT%

if not errorlevel 1 goto :end

echo.
echo [FAIL] Port %PORT% in use, trying port 9999 ...
"%PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port 9999

if not errorlevel 1 goto :end

echo.
echo =============================================
echo [ERROR] Both port %PORT% and 9999 are blocked
echo =============================================
echo.
echo Likely cause: Windows reserved these ports
echo (Hyper-V, WSL, or IIS).
echo.
echo To fix:
echo   1. Open .env with Notepad, change PORT=3000
echo   2. Save and double-click run.bat again
echo.
echo If 3000 also fails, try 3001, 5000, 8080, etc.
echo.

:end
pause
'@

# 写入 UTF-8 with BOM（Windows .bat 中文兼容性要求）
$Utf8Bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllText($RunBatPath, $runBatContent, $Utf8Bom)
Write-Host "  run.bat 已生成 (UTF-8 with BOM)." -ForegroundColor Green

# =============================================
# 完成
# =============================================
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "   Build Complete!" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Output: $DistDir" -ForegroundColor Green
Write-Host ""
Write-Host "  To test:" -ForegroundColor Gray
Write-Host "    cd dist\rag-qa-system-release" -ForegroundColor Gray
Write-Host "    run.bat" -ForegroundColor Gray
Write-Host ""