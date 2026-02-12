@echo off
chcp 65001 >nul
title Maestro WebUI - AI 创作平台

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🎭 MAESTRO - AI 创作平台                          ║
echo ║                                                              ║
echo ║     整合 LongCat-Video 和 SongGeneration 的统一界面        ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python 环境，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查 Gradio
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 Gradio...
    pip install gradio
)

echo [启动] 正在启动 Maestro WebUI...
echo.
echo 启动后请在浏览器中访问: http://localhost:7860
echo.

cd /d "%~dp0"
python app.py

pause



