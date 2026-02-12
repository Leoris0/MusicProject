#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🎭 MAESTRO - AI 创作平台                          ║"
echo "║                                                              ║"
echo "║     整合 LongCat-Video 和 SongGeneration 的统一界面        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "[错误] 未检测到 Python 环境，请先安装 Python 3.8+"
    exit 1
fi

# 检查 Gradio
python -c "import gradio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[提示] 正在安装 Gradio..."
    pip install gradio
fi

echo "[启动] 正在启动 Maestro WebUI..."
echo ""
echo "启动后请在浏览器中访问: http://localhost:7860"
echo ""

cd "$(dirname "$0")"
python app.py



