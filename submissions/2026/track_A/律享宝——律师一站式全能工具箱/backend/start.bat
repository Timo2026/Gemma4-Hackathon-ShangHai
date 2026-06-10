@echo off
chcp 65001 >nul
title 律享宝 - 后端启动器

echo ========================================
echo   律享宝 - 后端服务启动
echo ========================================
echo.

:: 检查 Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

:: 检查虚拟环境
if exist venv\Scripts\python.exe (
    echo [信息] 使用虚拟环境 venv
    set PYTHON=venv\Scripts\python.exe
) else (
    echo [信息] 使用系统 Python
    set PYTHON=python
)

:: 安装依赖
echo [步骤 1/3] 安装依赖...
%PYTHON% -m pip install -r requirements.txt -q
if %ERRORLEVEL% neq 0 (
    echo [警告] 部分依赖安装失败，尝试继续...
)

:: 检查 .env
if not exist .env (
    echo [警告] .env 文件不存在！请创建 .env 文件并配置 GMI_API_KEY
    echo.
    echo 参考模板：
    echo GMI_API_KEY=your_api_key_here
    echo GMI_BASE_URL=https://api.gmi.cloud/v1
    echo GMI_MODEL=deepseek-v4-flash
    echo.
)

:: 启动服务
echo.
echo [步骤 2/3] 初始化数据库...
%PYTHON% -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine); print('数据库表创建完成')"
if %ERRORLEVEL% neq 0 (
    echo [警告] 数据库初始化失败，请检查 MySQL 是否已启动
)

echo.
echo [步骤 3/3] 启动 Web 服务...
echo.
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

%PYTHON% -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
