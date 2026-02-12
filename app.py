"""
Maestro - 统一的 AI 创作平台
整合 LongCat-Video 和 SongGeneration 功能
"""
import os
import sys
import json
import time
import base64
from pathlib import Path

import gradio as gr

# 添加模块路径
WEBUI_DIR = Path(__file__).parent
sys.path.insert(0, str(WEBUI_DIR))

# 读取背景图片并转为 base64
BG_IMAGE_PATH = WEBUI_DIR / "static" / "bg.png"
BG_IMAGE_BASE64 = ""
if BG_IMAGE_PATH.exists():
    with open(BG_IMAGE_PATH, "rb") as f:
        BG_IMAGE_BASE64 = base64.b64encode(f.read()).decode("utf-8")

from modules.longcat_module import get_longcat_module, LongCatVideoModule
from modules.song_module import get_song_module, SongGenerationModule, AUTO_PROMPT_TYPES, GENERATION_TYPES
from modules.avatar_module import get_avatar_module, AvatarModule
from modules.rag_module import create_rag_interface, get_rag_js_logic


# ==================== 自定义 CSS 样式 ====================
# 生成 CSS（包含动态背景图片）
def get_custom_css():
    bg_style = ""
    if BG_IMAGE_BASE64:
        bg_style = f"""
/* 主容器背景 - 陕北风格 */
.gradio-container {{
    background-image: 
        linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.5)),
        url('data:image/png;base64,{BG_IMAGE_BASE64}') !important;
    background-repeat: no-repeat !important;
    background-position: center center !important;
    background-attachment: fixed !important;
    background-size: cover !important;
    min-height: 100vh !important;
    font-family: 'Rajdhani', sans-serif !important;
}}

/* 确保内部容器透明 */
.gradio-container > .main,
.gradio-container > div {{
    background: transparent !important;
}}
"""
    else:
        bg_style = """
/* 主容器背景 - 默认深色 */
.gradio-container {
    background: var(--dark-bg) !important;
    background-image: 
        radial-gradient(ellipse at 20% 80%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(139, 92, 246, 0.05) 0%, transparent 70%),
        linear-gradient(180deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%) !important;
    background-attachment: fixed !important;
    min-height: 100vh;
    font-family: 'Rajdhani', sans-serif !important;
}
"""
    
    return """
/* 导入 Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

/* 全局样式 */
:root, .gradio-container {
    /* 1. 重新定义你的深色主题色 */
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --dark-bg: #0a0a0f;
    --card-bg: rgba(20, 20, 35, 0.95);
    
    /* 2. 核心：强制覆盖 Gradio 默认的白色/灰色背景变量 */
    --body-background-fill: var(--dark-bg) !important;
    --block-background-fill: rgba(15, 15, 25, 0.6) !important; /* 去除组件默认白底 */
    --block-border-color: rgba(139, 92, 246, 0.3) !important;
    --block-label-background-fill: transparent !important;
    --input-background-fill: rgba(10, 10, 20, 0.8) !important; /* 输入框去白底 */
    
    /* 3. 字体颜色变量 */
    --body-text-color: #ffffff !important;
    --block-label-text-color: rgba(255, 255, 255, 0.7) !important;
    
    /* 4. 定义你的强调色 */
    --accent-cyan: #00f5ff;
    --accent-pink: #ff00ff;
    --accent-purple: #8b5cf6;
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --border-glow: rgba(139, 92, 246, 0.5);
}


/* ==================== 针对上传按钮的强制透明补丁 ==================== */
/* 修复上传区域（虚线框）内部的白色背景 */
.gradio-container button.svelte-116rqfv, 
.gradio-container button[class*="svelte-"],
.gradio-container .upload-button, 
.gradio-container .image-container button,
.gradio-container .video-container button,
.gradio-container .audio-container button {
    background-color: transparent !important; 
    background-image: none !important;
    border: 1px dashed rgba(139, 92, 246, 0.4) !important;
}

/* 修复上传后的预览区域背景 */
.image-frame, .video-frame, .audio-frame {
    background-color: transparent !important;
}
""" + bg_style + """
/* 标题样式 */
.main-title {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 3.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #00f5ff 0%, #8b5cf6 50%, #ff00ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.5rem !important;
    text-shadow: 0 0 30px rgba(139, 92, 246, 0.5);
    letter-spacing: 0.1em;
}

.subtitle {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.2rem !important;
    color: var(--text-secondary) !important;
    text-align: center;
    margin-bottom: 2rem !important;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

/* 标签页样式 */
.tabs {
    background: transparent !important;
}

.tab-nav {
    background: var(--card-bg) !important;
    border-radius: 16px 16px 0 0 !important;
    padding: 8px !important;
    border-bottom: 2px solid var(--border-glow) !important;
}

.tab-nav button {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    padding: 16px 32px !important;
    border-radius: 12px !important;
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
    margin: 4px !important;
    letter-spacing: 0.05em;
}

.tab-nav button:hover {
    background: rgba(139, 92, 246, 0.2) !important;
    color: var(--accent-cyan) !important;
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.3) !important;
}

.tab-nav button.selected {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.4) 0%, rgba(118, 75, 162, 0.4) 100%) !important;
    color: var(--text-primary) !important;
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 25px rgba(139, 92, 246, 0.5), inset 0 0 20px rgba(139, 92, 246, 0.1) !important;
}

/* 标签页内容 */
.tabitem {
    background: var(--card-bg) !important;
    border-radius: 0 0 16px 16px !important;
    padding: 24px !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    border-top: none !important;
}

/* 分组框样式 */
.gr-group {
    background: rgba(15, 15, 25, 0.8) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    padding: 20px !important;
    margin-bottom: 16px !important;
}

.gr-group:hover {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 30px rgba(139, 92, 246, 0.15) !important;
}

/* Accordion 样式 */
.gr-accordion {
    background: rgba(15, 15, 25, 0.9) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    overflow: hidden !important;
}

.gr-accordion > .label-wrap {
    background: linear-gradient(90deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%) !important;
    padding: 16px 20px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 500 !important;
    color: var(--accent-cyan) !important;
    border-bottom: 1px solid rgba(139, 92, 246, 0.2) !important;
}

/* 输入框样式 */
.gr-textbox, .gr-textarea {
    background: rgba(10, 10, 20, 0.9) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-family: 'Space Mono', monospace !important;
}

.gr-textbox:focus, .gr-textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.2), inset 0 0 10px rgba(0, 245, 255, 0.05) !important;
}

.gr-textbox textarea, .gr-textarea textarea {
    background: transparent !important;
    color: var(--text-primary) !important;
}

/* 标签样式 */
label {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: var(--text-secondary) !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* 滑块样式 */
.gr-slider input[type="range"] {
    background: linear-gradient(90deg, var(--accent-purple) 0%, var(--accent-cyan) 100%) !important;
    border-radius: 8px !important;
    height: 6px !important;
}

.gr-slider input[type="range"]::-webkit-slider-thumb {
    background: var(--accent-cyan) !important;
    border: 2px solid var(--dark-bg) !important;
    box-shadow: 0 0 15px var(--accent-cyan) !important;
    width: 20px !important;
    height: 20px !important;
}

/* 下拉菜单样式 */
.gr-dropdown {
    background: rgba(10, 10, 20, 0.9) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 12px !important;
}

.gr-dropdown select {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* 按钮样式 */
.gr-button {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 14px 28px !important;
    border-radius: 12px !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.gr-button.primary {
    background: linear-gradient(135deg, var(--accent-purple) 0%, #a855f7 50%, var(--accent-pink) 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
}

.gr-button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6), 0 0 40px rgba(139, 92, 246, 0.3) !important;
}

/* 模块入口按钮特殊样式 */
#video-enter-btn {
    width: 100% !important;
    margin-top: 20px !important;
    padding: 18px 36px !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
}

#video-enter-btn:hover {
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.7), 0 0 50px rgba(102, 126, 234, 0.4) !important;
    transform: translateY(-3px) !important;
}

#song-enter-btn {
    width: 100% !important;
    margin-top: 20px !important;
    padding: 18px 36px !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
    box-shadow: 0 6px 25px rgba(245, 147, 251, 0.5) !important;
}

#song-enter-btn:hover {
    box-shadow: 0 10px 40px rgba(245, 147, 251, 0.7), 0 0 50px rgba(245, 147, 251, 0.4) !important;
    transform: translateY(-3px) !important;
}

/* Avatar 入口按钮样式 */
#avatar-enter-btn {
    width: 100% !important;
    margin-top: 20px !important;
    padding: 18px 36px !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%) !important;
    box-shadow: 0 6px 25px rgba(0, 212, 170, 0.5) !important;
}

#avatar-enter-btn:hover {
    box-shadow: 0 10px 40px rgba(0, 212, 170, 0.7), 0 0 50px rgba(0, 212, 170, 0.4) !important;
    transform: translateY(-3px) !important;
}

/* 模块卡片容器 */
#module-cards {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    gap: 40px !important;
}

/* 生成音乐按钮特殊样式 */
#generate-song-btn {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
    font-size: 1.2rem !important;
    padding: 18px 40px !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    box-shadow: 0 8px 30px rgba(245, 147, 251, 0.4) !important;
}

#generate-song-btn:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 12px 40px rgba(245, 147, 251, 0.6), 0 0 50px rgba(245, 147, 251, 0.3) !important;
}

/* 优化滑块样式 */
.gr-slider {
    margin: 15px 0 !important;
}

.gr-slider label {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin-bottom: 8px !important;
}

/* 优化 Group 容器 */
.gr-group {
    padding: 20px !important;
    border-radius: 12px !important;
}

/* 优化 Radio 按钮组 */
.gr-radio label {
    font-size: 0.95rem !important;
    padding: 10px 18px !important;
}

/* 优化文本框 - 深色主题 */
.gr-textbox textarea,
.gr-textbox input,
textarea,
input[type="text"] {
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    background: rgba(15, 15, 25, 0.95) !important;
    color: #e0e0e0 !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 8px !important;
}

.gr-textbox textarea:focus,
.gr-textbox input:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.2) !important;
}

/* ============ 全局深色主题修复 ============ */

/* 所有容器深色背景 */
/* ============ 最终修复版：解决滑块闪烁 ============ */

/* 1. 核心修复：把所有布局骨架设为全透明，停止颜色叠加！ */
.block, .form, .wrap, .panel, 
div[class*="block"], div[class*="form"], div[class*="panel"],
.gradio-container .gap {
    background: transparent !important;
    border-color: transparent !important;
}

/* 2. 只给最外层的卡片容器上色（Group 和 Tab） */
.gr-group, .tabitem {
    background: rgba(15, 15, 25, 0.95) !important;
    border: 1px solid rgba(139, 92, 246, 0.25) !important;
    /* 强制 GPU 新建渲染层，隔离闪烁 */
    transform: translateZ(0); 
}

/* 3. 修复滑块背景：让滑块所在的直接容器透明 */
.gr-slider, .gr-slider > div {
    background: transparent !important;
    border: none !important;
}

/* 4. 精准修复输入框：只给输入框内部上色 */
.gr-textbox textarea, .gr-textbox input,
.gr-number input {
    background: rgba(10, 10, 18, 0.8) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
}

/* 深色下拉菜单 */
.gr-dropdown, .gr-dropdown .wrap, .gr-dropdown > div {
    background: rgba(15, 15, 25, 0.98) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

.gr-dropdown ul, .gr-dropdown [role="listbox"] {
    background: rgba(12, 12, 20, 0.99) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
}

.gr-dropdown li, .gr-dropdown [role="option"] {
    color: #e0e0e0 !important;
    background: transparent !important;
}

.gr-dropdown li:hover, .gr-dropdown [role="option"]:hover {
    background: rgba(139, 92, 246, 0.25) !important;
}

/* 深色音频组件 */
.gr-audio, .gr-audio > div, .gr-audio .wrap,
audio, .audio-container {
    background: rgba(12, 12, 20, 0.95) !important;
    border-color: rgba(0, 245, 255, 0.3) !important;
}

/* 深色视频组件 */
.gr-video, .gr-video > div, .gr-video .wrap {
    background: rgba(12, 12, 20, 0.95) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

/* 标签页深色风格 */
.gr-tab-nav, .tabs > div:first-child, [role="tablist"] {
    background: rgba(15, 15, 25, 0.9) !important;
    border-color: rgba(139, 92, 246, 0.2) !important;
}

.gr-tab-nav button, [role="tab"] {
    background: transparent !important;
    color: rgba(255, 255, 255, 0.6) !important;
}

.gr-tab-nav button.selected, [role="tab"][aria-selected="true"] {
    background: rgba(139, 92, 246, 0.25) !important;
    color: #fff !important;
    border-bottom: 2px solid #8b5cf6 !important;
}

/* 深色 Radio 和 Checkbox */
.gr-checkbox, .gr-radio,
.gr-checkbox > label, .gr-radio > label,
[role="radiogroup"], [role="radio"],
input[type="checkbox"], input[type="radio"] {
    background: transparent !important;
}

.gr-radio > label > span, .gr-checkbox > label > span {
    background: rgba(15, 15, 25, 0.95) !important;
    border-color: rgba(139, 92, 246, 0.4) !important;
}

/* Radio 按钮组深色 */
.gr-radio .wrap, .gr-radio > div {
    background: transparent !important;
}

/* ============ 🆕 Avatar 页面 Radio 按钮样式 (类似生成类型按钮) ============ */
/* Radio 组容器 */
.gr-radio,
.gr-radio > div,
.gr-radio .wrap,
[role="radiogroup"] {
    background: transparent !important;
    border: none !important;
    gap: 12px !important;
    display: flex !important;
    flex-wrap: wrap !important;
}

/* Radio 按钮主体样式 */
.gr-radio label,
.gr-radio .wrap label,
[role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    
    background: rgba(20, 20, 35, 0.8) !important;
    background-color: rgba(20, 20, 35, 0.8) !important;
    border: 1px solid rgba(139, 92, 246, 0.35) !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    min-width: 80px !important;
    
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    
    color: rgba(255, 255, 255, 0.7) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

/* Radio 按钮悬停状态 */
.gr-radio label:hover,
.gr-radio .wrap label:hover,
[role="radiogroup"] label:hover {
    background: rgba(139, 92, 246, 0.2) !important;
    border-color: rgba(0, 245, 255, 0.5) !important;
    color: #fff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(139, 92, 246, 0.25) !important;
}

/* Radio 按钮选中状态 - 渐变背景 */
.gr-radio input[type="radio"]:checked + span,
.gr-radio input[type="radio"]:checked + label,
.gr-radio label.selected,
[role="radio"][aria-checked="true"],
.gr-radio .wrap label.selected {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.9) 0%, rgba(245, 87, 108, 0.9) 100%) !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    color: #fff !important;
    font-weight: 700 !important;
    box-shadow: 0 0 25px rgba(139, 92, 246, 0.5), 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    transform: scale(1.02) !important;
}

/* 隐藏 Radio 按钮原生圆点 */
.gr-radio input[type="radio"] {
    display: none !important;
}

/* 修复 Radio 按钮内部 span */
.gr-radio label span,
.gr-radio .wrap label span {
    background: transparent !important;
    background-color: transparent !important;
}

/* 滑块深色背景 */
/* 确保滑块的包裹层是透明的 */
.gr-slider, .gr-slider > div, .gr-slider .wrap {
    background: transparent !important; 
    border: none !important;
}

.gr-slider input[type="range"] {
    background: rgba(139, 92, 246, 0.3) !important;
}

.gr-slider input[type="number"],
.gr-slider .gr-number input {
    background: rgba(10, 10, 18, 0.95) !important;
    color: #e0e0e0 !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

/* Group 容器深色 */
.gr-group {
    background: rgba(12, 12, 20, 0.9) !important;
    border: 1px solid rgba(139, 92, 246, 0.25) !important;
    border-radius: 10px !important;
}

/* Accordion 深色 */
.gr-accordion, .gr-accordion > div {
    background: rgba(15, 15, 25, 0.95) !important;
    border-color: rgba(139, 92, 246, 0.25) !important;
}

/* Markdown 深色 */
.gr-markdown, .prose {
    background: transparent !important;
    color: rgba(255, 255, 255, 0.85) !important;
}

/* 代码块深色 */
.gr-markdown pre, .gr-markdown code, pre, code {
    background: rgba(10, 10, 18, 0.95) !important;
    color: #e0e0e0 !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

/* 信息文字颜色 */
.gr-info, .info, span.info {
    color: rgba(255, 255, 255, 0.5) !important;
}

/* Label 颜色 */
label, label span {
    color: rgba(255, 255, 255, 0.8) !important;
}

/* 按钮二级深色 */
.gr-button.secondary, button.secondary {
    background: rgba(15, 15, 25, 0.95) !important;
    border-color: rgba(139, 92, 246, 0.4) !important;
    color: #e0e0e0 !important;
}

.gr-button.secondary:hover {
    background: rgba(139, 92, 246, 0.2) !important;
    border-color: rgba(139, 92, 246, 0.6) !important;
}

/* 输入区域聚焦效果 */
*:focus {
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3) !important;
}

/* 滚动条深色 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(15, 15, 25, 0.8);
}

::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.5);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(139, 92, 246, 0.7);
}

/* 图片上传区域 */
.gr-image, .gr-image > div, .gr-file, .gr-file > div {
    background: rgba(12, 12, 20, 0.95) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

/* 歌词输入框深色样式 */
#song-lyrics-input textarea {
    background: rgba(10, 10, 18, 0.95) !important;
    color: #e8e8e8 !important;
    border: 1px solid rgba(168, 85, 247, 0.4) !important;
    border-radius: 10px !important;
    padding: 15px !important;
}

#song-lyrics-input textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.3) !important;
}

#song-lyrics-input textarea::placeholder {
    color: rgba(255, 255, 255, 0.35) !important;
}

/* 紧凑型滑块 */
.gr-slider {
    padding: 5px 0 !important;
}

/* 紧凑页面容器 */
#song-page {
    max-height: calc(100vh - 100px);
    overflow: hidden;
}

/* 生成信息区域 */
#song-output-info {
    background: rgba(10, 10, 18, 0.95) !important;
    padding: 10px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0, 245, 255, 0.2) !important;
    font-size: 0.85rem !important;
    color: rgba(255, 255, 255, 0.6) !important;
    max-height: 80px;
    overflow-y: auto;
}

/* ============ 针对性修复 ============ */

/* 修复数字输入框 */
input[type="number"] {
    background: rgba(10, 10, 18, 0.98) !important;
    color: #e0e0e0 !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 6px !important;
}

/* 修复 tabpanel */
[role="tabpanel"] {
    background: rgba(15, 15, 25, 0.9) !important;
}

.gr-button.secondary {
    background: transparent !important;
    color: var(--accent-cyan) !important;
    border: 2px solid var(--accent-cyan) !important;
}

.gr-button.secondary:hover {
    background: rgba(0, 245, 255, 0.1) !important;
    box-shadow: 0 0 25px rgba(0, 245, 255, 0.3) !important;
}

/* 文件上传区域 */
.gr-file, .gr-image, .gr-audio, .gr-video {
    background: rgba(10, 10, 20, 0.8) !important;
    border: 2px dashed rgba(139, 92, 246, 0.4) !important;
    border-radius: 16px !important;
}

.gr-file:hover, .gr-image:hover, .gr-audio:hover, .gr-video:hover {
    border-color: var(--accent-cyan) !important;
    background: rgba(0, 245, 255, 0.05) !important;
    box-shadow: 0 0 30px rgba(0, 245, 255, 0.1) !important;
}

/* ============ 🆕 强制修复所有按钮和上传区域白色背景 ============ */
/* 修复上传区域内部按钮 */
.gr-file button,
.gr-image button,
.gr-audio button,
.gr-video button,
.gr-file .wrap button,
.gr-image .wrap button,
.gr-audio .wrap button,
.gr-video .wrap button {
    background: rgba(20, 20, 35, 0.9) !important;
    background-color: rgba(20, 20, 35, 0.9) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    color: rgba(255, 255, 255, 0.8) !important;
}

/* 修复所有 span 元素的白色背景 */
.gr-radio span,
.gr-checkbox span,
.gr-file span,
.gr-audio span {
    background: transparent !important;
    background-color: transparent !important;
}

/* 修复 Gradio 内部组件的白色背景 */
[class*="svelte-"] {
    --tw-bg-opacity: 0 !important;
}

/* 强制所有表单元素深色背景 */
.gr-form,
.gr-box,
.gr-panel,
.gr-input-label,
.gr-check-radio {
    background: transparent !important;
    background-color: transparent !important;
}

/* Checkbox 样式 */
.gr-checkbox {
    accent-color: var(--accent-purple) !important;
}

/* 分隔线 */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent 0%, var(--accent-purple) 50%, transparent 100%) !important;
    margin: 24px 0 !important;
}

/* 模块标题卡片 */
.module-header {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    border: 1px solid rgba(139, 92, 246, 0.3);
    text-align: center;
}

.module-title {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: var(--accent-cyan) !important;
    margin-bottom: 8px !important;
    letter-spacing: 0.1em;
}

.module-desc {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    color: var(--text-secondary) !important;
    line-height: 1.6;
}

/* 功能卡片图标 */
.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
    display: block;
}

/* 输出区域高亮 */
.output-panel {
    background: linear-gradient(135deg, rgba(0, 245, 255, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%) !important;
    border: 1px solid rgba(0, 245, 255, 0.3) !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

/* 进度条 */
.progress-bar {
    background: rgba(10, 10, 20, 0.8) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

.progress-bar .progress {
    background: linear-gradient(90deg, var(--accent-purple) 0%, var(--accent-cyan) 100%) !important;
    box-shadow: 0 0 20px var(--accent-cyan) !important;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .main-title {
        font-size: 2rem !important;
    }
    
    .tab-nav button {
        padding: 12px 16px !important;
        font-size: 0.9rem !important;
    }
}

/* ============ ⏬ 强制修复：下拉菜单向下展开 ⏬ ============ */

/* 1. 核心定位修复：强制在下方显示 */
.gr-dropdown .options, 
.gr-dropdown ul.options, 
ul.options {
    /* 关键属性：强制锁定在父容器的 100% 高度处（即底部） */
    top: 100% !important;      
    bottom: auto !important;    /* 禁止它向上弹出 */
    left: 0 !important;
    
    /* 视觉微调 */
    margin-top: 5px !important; /* 和输入框保持一点距离 */
    width: 100% !important;     /* 宽度和输入框对齐 */
    max-height: 250px !important; /* 限制高度，选项太多时显示滚动条 */
    overflow-y: auto !important;
    
    /* 2. 颜色修复：解决“白底白字”导致看不见的问题 */
    background-color: #0f0f19 !important; /* 深色背景 */
    border: 1px solid rgba(139, 92, 246, 0.5) !important; /* 紫色边框 */
    border-radius: 8px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important; /* 深色阴影 */
    z-index: 9999 !important; /* 保证显示在最上层，不被遮挡 */
}

/* 3. 选项文字修复 */
.gr-dropdown .item, 
.gr-dropdown li,
.gr-dropdown .options li {
    color: #e0e0e0 !important; /* 浅灰色文字 */
    background: transparent !important;
    padding: 10px 15px !important;
    font-size: 0.95rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
}

/* ============ 🆕 修复：右上角悬浮返回按钮 ============ */

/* 1. 定义头部容器为定位基准 */
#song-header-container {
    position: relative !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    overflow: visible !important; /* 允许按钮悬浮 */
}

/* 2. 将按钮绝对定位到右上角 */
#song-back-btn {
    position: absolute !important;
    top: 25px !important;    /* 距离顶部距离，根据标题栏高度微调 */
    right: 30px !important;  /* 距离右侧距离 */
    width: auto !important;
    background: rgba(0, 0, 0, 0.2) !important; /* 半透明黑底 */
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 20px !important; /* 圆角胶囊状 */
    color: rgba(255, 255, 255, 0.8) !important;
    padding: 8px 24px !important;
    z-index: 100 !important; /* 保证在最上层 */
    box-shadow: none !important;
    transition: all 0.3s ease !important;
}

/* 3. 鼠标悬停效果 */
#song-back-btn:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.6) !important;
    color: #fff !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3) !important;
}

/* ============ 🆕 视频页面：右上角悬浮返回按钮 ============ */

/* 1. 视频页面的头部容器定位基准 */
#video-header-container {
    position: relative !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    overflow: visible !important;
}

/* 2. 视频页面的返回按钮样式（复用之前的逻辑，改为对应ID） */
#video-back-btn-styled {
    position: absolute !important;
    top: 25px !important;
    right: 30px !important;
    width: auto !important;
    background: rgba(0, 0, 0, 0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 20px !important;
    color: rgba(255, 255, 255, 0.8) !important;
    padding: 8px 24px !important;
    z-index: 100 !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
}

#video-back-btn-styled:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.6) !important;
    color: #fff !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3) !important;
}

/* ============ 🆕 Avatar 页面：右上角悬浮返回按钮 ============ */

#avatar-header-container {
    position: relative !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    overflow: visible !important;
}

#avatar-back-btn {
    position: absolute !important;
    top: 25px !important;
    right: 30px !important;
    width: auto !important;
    background: rgba(0, 0, 0, 0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 20px !important;
    color: rgba(255, 255, 255, 0.8) !important;
    padding: 8px 24px !important;
    z-index: 100 !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
}

#avatar-back-btn:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.6) !important;
    color: #fff !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3) !important;
}


/* ============ 🆕 左下角“设置与帮助”浮动菜单 ============ */

/* 1. 隐藏 Gradio 默认的页脚 (API/Gradio链接) */
footer {
    display: none !important;
}

/* 2. 浮动菜单容器 */
.settings-container {
    position: fixed !important;
    bottom: 25px !important;
    left: 25px !important;
    z-index: 9999 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* 3. 触发按钮 (仿 Google 设计，但适配深色主题) */
.settings-btn {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    background: rgba(20, 20, 35, 0.9) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 30px !important; /* 胶囊形状 */
    padding: 10px 20px !important;
    color: rgba(255, 255, 255, 0.8) !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

.settings-btn:hover {
    background: rgba(139, 92, 246, 0.2) !important;
    border-color: rgba(139, 92, 246, 0.6) !important;
    color: #fff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.25) !important;
}

/* 图标旋转动画 */
.settings-btn:hover .settings-icon {
    transform: rotate(90deg);
}
.settings-icon {
    transition: transform 0.5s ease !important;
    font-size: 1.2rem !important;
}

/* 4. 弹出菜单 (默认隐藏，悬停显示) */
.settings-menu {
    position: absolute !important;
    bottom: 100% !important; /* 在按钮上方 */
    left: 0 !important;
    width: 260px !important;
    background: rgba(15, 15, 25, 0.98) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 16px !important;
    padding: 8px !important;
    margin-bottom: 12px !important;
    opacity: 0;
    visibility: hidden;
    transform: translateY(10px);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6) !important;
    backdrop-filter: blur(12px) !important;
}

/* 悬停容器时显示菜单 */
.settings-container:hover .settings-menu {
    opacity: 1 !important;
    visibility: visible !important;
    transform: translateY(0) !important;
}

/* 菜单项样式 */
.menu-item {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 12px 16px !important;
    color: #e0e0e0 !important;
    text-decoration: none !important;
    border-radius: 8px !important;
    transition: background 0.2s ease !important;
    font-size: 0.95rem !important;
    cursor: pointer !important;
}

.menu-item:hover {
    background: rgba(139, 92, 246, 0.15) !important;
    color: #00f5ff !important;
}

.menu-item span {
    font-size: 1.1rem !important;
    width: 24px;
    text-align: center;
}

/* 分隔线 */
.menu-divider {
    height: 1px !important;
    background: rgba(255, 255, 255, 0.1) !important;
    margin: 6px 0 !important;
}

/* 菜单头部信息 */
.menu-header {
    padding: 12px 16px !important;
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 0.8rem !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    margin-bottom: 6px !important;
}
/* ============ 🆕 简洁版：生成类型容器适配 ============ */

/* 1. 容器清理：确保和上面的标题无缝衔接 */
#gen-type-radio {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-top: -5px !important; /* 稍微往上拉一点，紧贴标题 */
}

/* 2. 按钮容器布局 */
#gen-type-radio .wrap {
    background: transparent !important;
    gap: 15px !important; 
    display: flex !important;
    flex-wrap: wrap !important;
}

/* 3. 按钮主体样式 (保持你喜欢的霓虹卡片风) */
#gen-type-radio .wrap label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    
    background: rgba(20, 20, 35, 0.6) !important; 
    border: 1px solid rgba(139, 92, 246, 0.3) !important; 
    border-radius: 12px !important;
    padding: 14px 20px !important;
    
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    
    color: rgba(255, 255, 255, 0.6) !important; 
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
}

/* 4. 鼠标悬停 */
#gen-type-radio .wrap label:hover {
    background: rgba(139, 92, 246, 0.15) !important;
    border-color: rgba(0, 245, 255, 0.6) !important;
    color: #fff !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 245, 255, 0.15) !important;
}

/* 5. 选中状态 */
#gen-type-radio .wrap label.selected, 
#gen-type-radio input:checked + label {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.9) 0%, rgba(245, 87, 108, 0.9) 100%) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
    color: #fff !important;
    box-shadow: 0 0 25px rgba(245, 87, 108, 0.5) !important;
    font-weight: 700 !important;
    transform: scale(1.02) !important;
}

/* 6. 说明文字样式 (info) */
#gen-type-radio .info {
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 0.85rem !important;
    margin-bottom: 12px !important;
    word-spacing: 15px !important;   
}

/* 7. 隐藏不需要的元素 */
#gen-type-radio input[type="radio"],
#gen-type-radio .ml-2 {
    display: none !important;
}

/* 1. 容器重置 */
#resolution-group {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-top: 10px !important;
}

#resolution-group .wrap {
    background: transparent !important;
    gap: 10px !important; /* 按钮之间的间距 */
    display: flex !important;
    flex-wrap: wrap !important;
}

/* 2. 按钮主体：深色玻璃质感 */
#resolution-group label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    
    background: rgba(20, 20, 35, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 8px !important; /* 稍微小一点的圆角 */
    padding: 8px 20px !important;  /* 紧凑一点的内边距 */
    
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    
    color: rgba(255, 255, 255, 0.7) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
}

/* 3. 鼠标悬停 */
#resolution-group label:hover {
    background: rgba(139, 92, 246, 0.2) !important;
    border-color: rgba(0, 245, 255, 0.6) !important;
    color: #fff !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 245, 255, 0.2) !important;
}

/* 4. 选中状态：渐变高亮 */
#resolution-group label.selected,
#resolution-group input:checked + label {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%) !important; /* 蓝紫渐变 */
    border-color: rgba(255, 255, 255, 0.4) !important;
    color: #fff !important;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.5) !important;
    font-weight: 700 !important;
}

/* 5. 隐藏原生圆点 */
#resolution-group input[type="radio"],
#resolution-group .ml-2,
#resolution-group span.circle {
    display: none !important;
}

/* ============ 🆕 修复：通用选项按钮美化 (分辨率/模式) ============ */

/* 1. 容器重置 */
#resolution-group {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-top: 10px !important;
}

#resolution-group .wrap {
    background: transparent !important;
    gap: 10px !important; /* 按钮之间的间距 */
    display: flex !important;
    flex-wrap: wrap !important;
}

/* 2. 按钮主体：深色玻璃质感 */
#resolution-group label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    
    background: rgba(20, 20, 35, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 8px !important; /* 稍微小一点的圆角 */
    padding: 8px 20px !important;  /* 紧凑一点的内边距 */
    
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    
    color: rgba(255, 255, 255, 0.7) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
}

/* 3. 鼠标悬停 */
#resolution-group label:hover {
    background: rgba(139, 92, 246, 0.2) !important;
    border-color: rgba(0, 245, 255, 0.6) !important;
    color: #fff !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 245, 255, 0.2) !important;
}

/* 4. 选中状态：渐变高亮 */
#resolution-group label.selected,
#resolution-group input:checked + label {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%) !important; /* 蓝紫渐变，区别于音乐页面的紫红 */
    border-color: rgba(255, 255, 255, 0.4) !important;
    color: #fff !important;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.5) !important;
    font-weight: 700 !important;
}

/* 5. 隐藏原生圆点 */
#resolution-group input[type="radio"],
#resolution-group .ml-2,
#resolution-group span.circle {
    display: none !important;
}

/* ============ 🆕 修复：音频模式字体与按钮美化 ============ */

/* 1. 让标题 "音频模式" 的字体大小、粗细完全复制 "场景描述" */
#audio-mode-radio .block-label {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;      /* 核心：强制设为 1rem (和场景描述一致) */
    color: var(--text-secondary) !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* 2. 让说明文字 "para: 并行..." 也变大、变清晰 */
#audio-mode-radio .info {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.9rem !important;    /*稍微比标题小一点点，或者设为 1rem 就完全一样大 */
    color: rgba(255, 255, 255, 0.5) !important;
    margin-bottom: 12px !important;
    margin-top: 0 !important;
}

/* 3. 顺便把下面的按钮也美化成“霓虹卡片”风格（和之前建议的分辨率按钮一样） */
#audio-mode-radio .wrap {
    display: flex !important;
    gap: 15px !important;
    background: transparent !important;
}

#audio-mode-radio label {
    background: rgba(20, 20, 35, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    color: rgba(255, 255, 255, 0.7) !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
    
    /* 弹性布局居中文字 */
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

/* 选中状态：紫色渐变 */
#audio-mode-radio label.selected,
#audio-mode-radio input:checked + label {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
    color: #fff !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.4) !important;
}

/* 隐藏原生小圆点 */
#audio-mode-radio input[type="radio"],
#audio-mode-radio span.circle {
    display: none !important;
}
"""

# ==================== 辅助函数 ====================

def create_result_info(config, success=True):
    """创建结果信息"""
    if success and config.get("success"):
        return f"""
## ✅ 生成成功！

- 输出文件: `{config.get('output_path', 'N/A')}`
- 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    elif config.get("error"):
        return f"""
## ❌ 生成失败

错误信息: {config.get('error')}

{config.get('note', '')}
"""
    else:
        note = config.get('note', '')
        return f"""
## ⚠️ 配置已生成

{note}

```json
{json.dumps(config, ensure_ascii=False, indent=2)}
```
"""

# ==================== LongCat-Video 功能函数 ====================

def longcat_text_to_video(prompt, negative_prompt, height, width, num_frames,
                          num_inference_steps, guidance_scale, seed, use_distill,
                          progress=gr.Progress()):
    """文本生成视频 - 真正的模型推理"""
    progress(0, desc="初始化...")
    
    if not prompt or not prompt.strip():
        return None, "❌ 请输入视频描述"
    
    try:
        module = get_longcat_module()
        
        def progress_wrapper(value, desc=""):
            progress(value, desc=desc)
        
        output_path, config = module.text_to_video(
            prompt=prompt,
            negative_prompt=negative_prompt,
            height=int(height),
            width=int(width),
            num_frames=int(num_frames),
            num_inference_steps=int(num_inference_steps),
            guidance_scale=float(guidance_scale),
            seed=int(seed),
            use_distill=use_distill,
            progress_callback=progress_wrapper
        )
        
        progress(1.0, desc="完成!")
        
        # 返回实际生成的视频文件
        if output_path and os.path.exists(output_path):
            result_info = create_result_info(config, success=True)
            return output_path, result_info
        else:
            result_info = create_result_info(config, success=False)
            return None, result_info
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ 错误: {str(e)}"

def longcat_image_to_video(image, prompt, negative_prompt, resolution, num_frames,
                           num_inference_steps, guidance_scale, seed, use_distill,
                           progress=gr.Progress()):
    """图片生成视频 - 真正的模型推理"""
    progress(0, desc="初始化...")
    
    if image is None:
        return None, "❌ 请上传一张图片"
    
    try:
        module = get_longcat_module()
        
        def progress_wrapper(value, desc=""):
            progress(value, desc=desc)
        
        output_path, config = module.image_to_video(
            image_path=image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            resolution=resolution,
            num_frames=int(num_frames),
            num_inference_steps=int(num_inference_steps),
            guidance_scale=float(guidance_scale),
            seed=int(seed),
            use_distill=use_distill,
            progress_callback=progress_wrapper
        )
        
        progress(1.0, desc="完成!")
        
        if output_path and os.path.exists(output_path):
            result_info = create_result_info(config, success=True)
            return output_path, result_info
        else:
            result_info = create_result_info(config, success=False)
            return None, result_info
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ 错误: {str(e)}"

def longcat_audio_to_video(audio, image, prompt, resolution, num_frames,
                           num_inference_steps, text_guidance, audio_guidance,
                           seed, num_segments, stage,
                           progress=gr.Progress()):
    """音频驱动数字人视频生成"""
    progress(0, desc="初始化...")
    
    if audio is None:
        return None, "❌ 请上传音频文件"
    
    if stage == "ai2v" and image is None:
        return None, "❌ ai2v 模式需要上传参考图片"
    
    try:
        module = get_avatar_module()
        
        def progress_wrapper(value, desc=""):
            progress(value, desc=desc)
        
        output_path, config = module.single_avatar(
            audio_path=audio,
            image_path=image,
            prompt=prompt,
            stage_1=stage,
            resolution=resolution,
            num_inference_steps=int(num_inference_steps),
            text_guidance_scale=float(text_guidance),
            audio_guidance_scale=float(audio_guidance),
            seed=int(seed),
            num_segments=int(num_segments),
            progress_callback=progress_wrapper
        )
        
        progress(1.0, desc="完成!")
        
        if output_path and os.path.exists(output_path):
            result_info = create_result_info(config, success=True)
            return output_path, result_info
        else:
            result_info = create_result_info(config, success=False)
            return None, result_info
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ 错误: {str(e)}"

# ==================== SongGeneration 功能函数 ====================

def song_generate(lyrics, description, prompt_audio, auto_style, gen_type,
                  max_duration, cfg_coef, temperature, top_k, top_p, low_mem,
                  progress=gr.Progress()):
    """生成歌曲 - 真正的模型推理"""
    progress(0, desc="初始化...")
    
    if not lyrics or not lyrics.strip():
        return None, "❌ 请输入歌词"
    
    try:
        module = get_song_module()
        
        def progress_wrapper(value, desc=""):
            progress(value, desc=desc)
        
        # 处理风格选择 - 优先级：参考音频 > 自动风格 > 文本描述
        prompt_audio_path = None
        auto_prompt_type = None
        desc = None
        
        if prompt_audio:
            # 使用上传的参考音频
            prompt_audio_path = prompt_audio
        elif auto_style and auto_style != "None":
            # 使用自动风格
            auto_prompt_type = auto_style
        
        if description and description.strip():
            # 文本描述可以和其他选项一起使用
            desc = description.strip()
        
        output_path, config = module.generate_song(
            lyrics=lyrics,
            description=desc,
            prompt_audio_path=prompt_audio_path,
            auto_prompt_type=auto_prompt_type,
            gen_type=gen_type,
            max_duration=int(max_duration),
            cfg_coef=float(cfg_coef),
            temperature=float(temperature),
            top_k=int(top_k),
            top_p=float(top_p),
            low_mem=low_mem,
            progress_callback=progress_wrapper
        )
        
        progress(1.0, desc="完成!")
        
        # 返回实际生成的音频文件
        if output_path and os.path.exists(output_path):
            result_info = create_result_info(config, success=True)
            return output_path, result_info
        else:
            result_info = create_result_info(config, success=False)
            return None, result_info
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ 错误: {str(e)}"

def song_format_lyrics(raw_lyrics):
    """格式化歌词"""
    try:
        module = get_song_module()
        formatted = module.format_lyrics(raw_lyrics)
        return formatted
    except Exception as e:
        return f"格式化错误: {str(e)}"

def song_load_example():
    """加载示例歌词"""
    module = get_song_module()
    return module.get_example_lyrics()

# ==================== Avatar 功能函数 ====================

def avatar_single_generate(audio, image, prompt, stage_1, resolution, 
                           num_inference_steps, text_guidance, audio_guidance,
                           seed, num_segments, ref_img_index, mask_frame_range,
                           progress=gr.Progress()):
    """单人说话视频生成"""
    progress(0, desc="初始化...")
    
    if audio is None:
        return None, "❌ 请上传音频文件"
    
    if stage_1 == "ai2v" and image is None:
        return None, "❌ ai2v 模式需要上传参考图片"
    
    try:
        module = get_avatar_module()
        
        def progress_wrapper(value, desc=""):
            progress(value, desc=desc)
        
        output_path, config = module.single_avatar(
            audio_path=audio,
            image_path=image,
            prompt=prompt,
            stage_1=stage_1,
            resolution=resolution,
            num_inference_steps=int(num_inference_steps),
            text_guidance_scale=float(text_guidance),
            audio_guidance_scale=float(audio_guidance),
            seed=int(seed),
            num_segments=int(num_segments),
            ref_img_index=int(ref_img_index),
            mask_frame_range=int(mask_frame_range),
            progress_callback=progress_wrapper
        )
        
        progress(1.0, desc="完成!")
        
        if output_path and os.path.exists(output_path):
            result_info = create_result_info(config, success=True)
            return output_path, result_info
        else:
            result_info = create_result_info(config, success=False)
            return None, result_info
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ 错误: {str(e)}"


def avatar_multi_generate(image, audio1, audio2, prompt, audio_type, resolution,
                          num_inference_steps, text_guidance, audio_guidance,
                          seed, num_segments, ref_img_index, mask_frame_range,
                          bbox1_str, bbox2_str, progress=gr.Progress()):
    """双人对话视频生成"""
    progress(0, desc="初始化...")
    
    if image is None:
        return None, "❌ 请上传参考图片"
    
    if audio1 is None and audio2 is None:
        return None, "❌ 至少需要上传一个音频文件"
    
    try:
        module = get_avatar_module()
        
        def progress_wrapper(value, desc=""):
            progress(value, desc=desc)
        
        # 解析 bbox
        bbox1 = None
        bbox2 = None
        if bbox1_str and bbox1_str.strip():
            bbox1 = [int(x.strip()) for x in bbox1_str.split(',')]
        if bbox2_str and bbox2_str.strip():
            bbox2 = [int(x.strip()) for x in bbox2_str.split(',')]
        
        output_path, config = module.multi_avatar(
            image_path=image,
            audio1_path=audio1,
            audio2_path=audio2,
            prompt=prompt,
            audio_type=audio_type,
            resolution=resolution,
            num_inference_steps=int(num_inference_steps),
            text_guidance_scale=float(text_guidance),
            audio_guidance_scale=float(audio_guidance),
            seed=int(seed),
            num_segments=int(num_segments),
            ref_img_index=int(ref_img_index),
            mask_frame_range=int(mask_frame_range),
            bbox1=bbox1,
            bbox2=bbox2,
            progress_callback=progress_wrapper
        )
        
        progress(1.0, desc="完成!")
        
        if output_path and os.path.exists(output_path):
            result_info = create_result_info(config, success=True)
            return output_path, result_info
        else:
            result_info = create_result_info(config, success=False)
            return None, result_info
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ 错误: {str(e)}"

# ==================== 创建 Gradio 界面 ====================

def create_app():
    """创建主应用"""
    
    with gr.Blocks(title="Maestro - AI 创作平台") as app:
        
        # 注入 AI 助手 UI 及相关逻辑
        create_rag_interface()

        # 页面状态管理
        current_page = gr.State("home")
        
        # ==================== 主页/入口页面 ====================
        with gr.Column(visible=True, elem_id="home-page") as home_page:
            # 标题
            gr.HTML("""
            <div style="text-align: center; padding: 60px 20px 40px 20px;">
                <p style="background: linear-gradient(90deg, #6366f1 0%, #a855f7 35%, #ec4899 70%, #ef4444 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; color: transparent; font-size: 3rem; margin-top: 15px; letter-spacing: 0.1em; font-weight: bold;">
                    陕北民歌・声影工坊
                </p>
            </div>
            """)
            
            # 模块选择卡片
            gr.HTML("""
            <div style="text-align: center; margin: 40px auto 20px auto; max-width: 1200px;">
                <h2 style="font-family: 'Orbitron', sans-serif; font-size: 1.5rem; color: var(--accent-cyan); margin-bottom: 30px; letter-spacing: 0.1em;">
                    ✨ 让灵感在此流淌 ✨
                </h2>
            </div>
            """)
            
            with gr.Row(equal_height=True, elem_id="module-cards"):
                # LongCat-Video 模块卡片
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style="
                        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.2) 100%);
                        border: 2px solid rgba(102, 126, 234, 0.5);
                        border-radius: 24px;
                        padding: 40px 30px;
                        text-align: center;
                        transition: all 0.3s ease;
                        cursor: pointer;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    " onmouseover="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 40px rgba(102, 126, 234, 0.4)'; this.style.transform='translateY(-5px)';" onmouseout="this.style.borderColor='rgba(102, 126, 234, 0.5)'; this.style.boxShadow='none'; this.style.transform='translateY(0)';">
                        <div style="font-size: 4rem; margin-bottom: 20px;">🎬</div>
                        <h3 style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; color: #667eea; margin-bottom: 15px; letter-spacing: 0.05em;">
                            无声流影视界
                        </h3>
                        <p style="font-family: 'Rajdhani', sans-serif; color: rgba(255,255,255,0.7); font-size: 1.1rem; line-height: 1.8; margin-bottom: 25px;">
                            Motion from Imagination
                        </p>
                        <div style="text-align: left; margin: 0 auto; max-width: 300px;">
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                ✨ 文本生成意境
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                ✨ 图片演化动态
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                ✨ 纯视觉沉浸体验
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                ✨ 多风格生成
                            </div>
                        </div>
                    </div>
                    """)
                    video_enter_btn = gr.Button("🎬 进入无声视频生成", variant="primary", size="lg", elem_id="video-enter-btn")
                
                # SongGeneration 模块卡片
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style="
                        background: linear-gradient(135deg, rgba(245, 147, 251, 0.15) 0%, rgba(245, 87, 108, 0.2) 100%);
                        border: 2px solid rgba(245, 147, 251, 0.5);
                        border-radius: 24px;
                        padding: 40px 30px;
                        text-align: center;
                        transition: all 0.3s ease;
                        cursor: pointer;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    " onmouseover="this.style.borderColor='#f093fb'; this.style.boxShadow='0 0 40px rgba(245, 147, 251, 0.4)'; this.style.transform='translateY(-5px)';" onmouseout="this.style.borderColor='rgba(245, 147, 251, 0.5)'; this.style.boxShadow='none'; this.style.transform='translateY(0)';">
                        <div style="font-size: 4rem; margin-bottom: 20px;">🎵</div>
                        <h3 style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; color: #f093fb; margin-bottom: 15px; letter-spacing: 0.05em;">
                            灵感作曲核心
                        </h3>
                        <p style="font-family: 'Rajdhani', sans-serif; color: rgba(255,255,255,0.7); font-size: 1.1rem; line-height: 1.8; margin-bottom: 25px;">
                            Melody from Text & Lyrics
                        </p>
                        <div style="text-align: left; margin: 0 auto; max-width: 300px;">
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎼 歌词生成歌曲
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎼 多种音乐风格
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎼 人声伴奏分离
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎼 风格迁移转换
                            </div>
                        </div>
                    </div>
                    """)
                    song_enter_btn = gr.Button("🎵 进入歌曲生成", variant="primary", size="lg", elem_id="song-enter-btn")
                
                # Avatar 模块卡片
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style="
                        background: linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(0, 184, 148, 0.2) 100%);
                        border: 2px solid rgba(0, 212, 170, 0.5);
                        border-radius: 24px;
                        padding: 40px 30px;
                        text-align: center;
                        transition: all 0.3s ease;
                        cursor: pointer;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    " onmouseover="this.style.borderColor='#00d4aa'; this.style.boxShadow='0 0 40px rgba(0, 212, 170, 0.4)'; this.style.transform='translateY(-5px)';" onmouseout="this.style.borderColor='rgba(0, 212, 170, 0.5)'; this.style.boxShadow='none'; this.style.transform='translateY(0)';">
                        <div style="font-size: 4rem; margin-bottom: 20px;">🎼</div>
                        <h3 style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; color: #00d4aa; margin-bottom: 15px; letter-spacing: 0.05em;">
                            歌韵织绘成影
                        </h3>
                        <p style="font-family: 'Rajdhani', sans-serif; color: rgba(255,255,255,0.7); font-size: 1.1rem; line-height: 1.8; margin-bottom: 25px;">
                            Avatar Speaking Video
                        </p>
                        <div style="text-align: left; margin: 0 auto; max-width: 300px;">
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎤 单人演唱视频生成
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎤 双人对唱视频生成
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎤 唇形精准同步
                            </div>
                            <div style="margin: 10px 0; color: rgba(255,255,255,0.6); font-size: 0.95rem;">
                                🎤 长视频续写
                            </div>
                        </div>
                    </div>
                    """)
                    avatar_enter_btn = gr.Button("🎼 进入有声视频生成", variant="primary", size="lg", elem_id="avatar-enter-btn")

            # 页脚信息
            gr.HTML("""
            <div style="text-align: center; padding: 40px 20px; margin-top: 60px;">
                <p style="color: rgba(255,255,255,0.4); font-size: 0.9rem; margin-bottom: 10px;">
                    💡 提示：AI生成内容仅供参考，请勿用于非法用途
                </p>
                <p style="color: rgba(255,255,255,0.3); font-size: 0.85rem;">
                    2026 长安大学 大数据研究中心 版权所有
                </p>
            </div>
            """)
        
        # ==================== 视频生成页面 ====================
        with gr.Column(visible=False, elem_id="video-page") as video_page:
            # 🆕 修改：添加头部定位容器
            with gr.Column(elem_id="video-header-container"):
                # 1. 升级版标题栏 HTML (蓝紫色调，与音乐页面风格统一)
                gr.HTML("""
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 20px 30px; 
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
                border-radius: 16px; margin-bottom: 25px; border: 1px solid rgba(102, 126, 234, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));">🎬</span>
                        <div>
                            <h1 style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; 
                            background: linear-gradient(135deg, #00f5ff 0%, #8b5cf6 100%); 
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                            letter-spacing: 0.05em; margin: 0; font-weight: 800;">
                                无声流影视界
                            </h1>
                            <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 5px 0 0 0; letter-spacing: 0.1em;">
                                LongCat-Video Generation Engine
                            </p>
                        </div>
                    </div>
                </div>
                """)

                # 2. 放入按钮并指定 elem_id，使其悬浮到右上角
                video_back_btn = gr.Button("↩️ 返回主页", size="sm", elem_id="video-back-btn-styled")


            # 视频生成功能标签页
            with gr.Tabs() as video_function_tabs:
                    
                    # 文本生成视频
                    with gr.TabItem("📝 文本生成视频", id="t2v"):
                        with gr.Row():
                            with gr.Column(scale=1):
                                t2v_prompt = gr.Textbox(
                                    label="视频描述",
                                    placeholder="详细描述你想要生成的视频内容...",
                                    lines=4,

                                )
                                t2v_negative = gr.Textbox(
                                    label="负面提示词",
                                    placeholder="描述你不想在视频中出现的内容...",
                                    lines=2,

                                )
                                
                                with gr.Accordion("⚙️ 高级参数", open=False):
                                    with gr.Row():
                                        t2v_height = gr.Slider(240, 720, value=480, step=16, label="高度")
                                        t2v_width = gr.Slider(320, 1280, value=832, step=16, label="宽度")
                                    with gr.Row():
                                        t2v_frames = gr.Slider(16, 256, value=93, step=1, label="帧数")
                                        t2v_steps = gr.Slider(10, 100, value=50, step=1, label="推理步数")
                                    with gr.Row():
                                        t2v_guidance = gr.Slider(1.0, 15.0, value=4.0, step=0.1, label="引导比例")
                                        t2v_seed = gr.Number(value=42, label="随机种子")
                                    t2v_distill = gr.Checkbox(label="使用蒸馏模式 (更快)", value=False)
                                
                                t2v_btn = gr.Button("🎬 生成视频", variant="primary", size="lg")
                            
                            with gr.Column(scale=1):
                                t2v_output_video = gr.Video(label="生成结果", elem_id="t2v-output")
                                t2v_output_info = gr.Markdown(label="生成信息")
                        
                        t2v_btn.click(
                            fn=longcat_text_to_video,
                            inputs=[t2v_prompt, t2v_negative, t2v_height, t2v_width, 
                                   t2v_frames, t2v_steps, t2v_guidance, t2v_seed, t2v_distill],
                            outputs=[t2v_output_video, t2v_output_info]
                        )
                    
                    # 图片生成视频
                    with gr.TabItem("🖼️ 图片生成视频", id="i2v"):
                        with gr.Row():
                            with gr.Column(scale=1):
                                i2v_image = gr.Image(label="上传图片", type="filepath", elem_id="i2v-image")
                                i2v_prompt = gr.Textbox(
                                    label="动作描述",
                                    placeholder="描述图片中物体/人物的动作...",
                                    lines=3,

                                )
                                i2v_negative = gr.Textbox(
                                    label="负面提示词",
                                    lines=2,

                                )
                                
                                with gr.Accordion("⚙️ 高级参数", open=False):
                                    i2v_resolution = gr.Radio(["480p", "720p"], value="480p", label="分辨率",
                                                              elem_id="resolution-group")
                                    with gr.Row():
                                        i2v_frames = gr.Slider(16, 256, value=93, step=1, label="帧数")
                                        i2v_steps = gr.Slider(10, 100, value=50, step=1, label="推理步数")
                                    with gr.Row():
                                        i2v_guidance = gr.Slider(1.0, 15.0, value=4.0, step=0.1, label="引导比例")
                                        i2v_seed = gr.Number(value=42, label="随机种子")
                                    i2v_distill = gr.Checkbox(label="使用蒸馏模式", value=False)
                                
                                i2v_btn = gr.Button("🎬 生成视频", variant="primary", size="lg")
                            
                            with gr.Column(scale=1):
                                i2v_output_video = gr.Video(label="生成结果", elem_id="i2v-output")
                                i2v_output_info = gr.Markdown(label="生成信息")
                        
                        i2v_btn.click(
                            fn=longcat_image_to_video,
                            inputs=[i2v_image, i2v_prompt, i2v_negative, i2v_resolution,
                                   i2v_frames, i2v_steps, i2v_guidance, i2v_seed, i2v_distill],
                            outputs=[i2v_output_video, i2v_output_info]
                        )

                # ==================== 歌曲生成页面 ====================
        with gr.Column(visible=False, elem_id="song-page") as song_page:
        # 🆕 必须修改：添加这个容器，CSS 才能把按钮定位到右上角
            with gr.Column(elem_id="song-header-container"):
            # 标题栏 HTML (样式微调过，更美观)
                gr.HTML("""
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 20px 30px; 
                background: linear-gradient(135deg, rgba(245, 147, 251, 0.15) 0%, rgba(245, 87, 108, 0.1) 100%);
                border-radius: 16px; margin-bottom: 25px; border: 1px solid rgba(245, 147, 251, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(245, 147, 251, 0.5));">🎵</span>
                        <div>
                            <h1 style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; 
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                            letter-spacing: 0.05em; margin: 0; font-weight: 800;">
                                灵感作曲核心
                            </h1>
                            <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 5px 0 0 0; letter-spacing: 0.1em;">
                                Melody-Image Symbiosis System
                            </p>
                        </div>
                    </div>
                </div>
                """)

                # 🆕 关键点：按钮移到了这里，并且加了 elem_id="song-back-btn"
                song_back_btn = gr.Button("↩️ 返回主页", size="sm", elem_id="song-back-btn")


            with gr.Row(equal_height=True):
                # 左侧：歌词
                with gr.Column(scale=4):
                    gr.HTML("""<div style="color: #a855f7; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">📝 歌词</div>""")
                    
                    song_lyrics = gr.Textbox(
                        placeholder="""[verse] 雪花飞舞 ; [chorus] 这是美丽的冬天\n\n格式：[verse]、[chorus]、[bridge] 需要歌词，[intro]、[inst]、[outro] 不需要歌词""",
                        lines=6,
                        show_label=False,
                        elem_id="song-lyrics-input"
                    )
                    
                    # 风格设置区域 - 紧凑版
                    gr.HTML("""<div style="color: #f093fb; font-weight: 600; font-size: 1rem; margin: 12px 0 8px 0;">🎨 风格设置</div>""")
                    
                    with gr.Tabs() as song_style_tabs:
                        with gr.TabItem("📝 文本"):
                            song_description = gr.Textbox(
                                placeholder="female, dark, pop, sad, piano and drums, the bpm is 125",
                                lines=2,
                                show_label=False
                            )
                        
                        with gr.TabItem("🎭 风格"):
                            song_auto_style = gr.Dropdown(
                                choices=AUTO_PROMPT_TYPES,
                                value="Pop",
                                show_label=False
                            )
                        
                        with gr.TabItem("🎵 音频"):
                            song_prompt_audio = gr.Audio(
                                label="上传参考音频",
                                type="filepath"
                            )
                
                # 中间：参数
                with gr.Column(scale=3):
                    gr.HTML("""<div style="color: #ff9800; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">⚙️ 参数</div>""")
                    
                    with gr.Group():
                        song_max_duration = gr.Slider(30, 300, value=120, step=5, label="⏱️ 时长(秒)")
                        song_cfg = gr.Slider(0.1, 10.0, value=1.5, step=0.1, label="🎯 CFG")
                        song_temp = gr.Slider(0.1, 2.0, value=0.9, step=0.05, label="🌡️ 温度")
                        song_top_k = gr.Slider(0, 200, value=50, step=1, label="Top-K")
                        song_top_p = gr.Slider(0.0, 1.0, value=0.0, step=0.01, label="Top-P")


                    # 1. 插入一个新的 HTML 标题 (完全复制"参数"的样式，只改文字)
                    gr.HTML(
                        """<div style="color: #ff9800; font-weight: 600; font-size: 1rem; margin-bottom: 8px; margin-top: 15px;">🎹 生成类型</div>""")

                    # 2. 修改 Radio 组件 (隐藏自带的 label)
                    song_gen_type = gr.Radio(
                        GENERATION_TYPES,
                        value="mixed",
                        show_label=False,  # ⬅️ 关键：隐藏自带标签，使用上面的 HTML 代替
                        info="mixed:混合  |  vocal:人声  |  bgm:伴奏  |  separate:分离",
                        elem_id="gen-type-radio"
                    )

                    
                    song_low_mem = gr.Checkbox(label="💾 低显存模式", value=False)
                
                # 右侧：操作和结果
                with gr.Column(scale=3):
                    gr.HTML("""<div style="color: #00f5ff; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">🎵 生成</div>""")
                    
                    song_btn = gr.Button("🎵 生成音乐", variant="primary", size="lg", elem_id="generate-song-btn")
                    
                    with gr.Row():
                        song_load_example_btn = gr.Button("📋 示例", size="sm")
                        song_format_btn = gr.Button("✨ 格式化", size="sm")
                    
                    gr.HTML("""<div style="color: #00f5ff; font-weight: 600; font-size: 0.95rem; margin: 15px 0 8px 0;">🔊 结果</div>""")
                    song_output_audio = gr.Audio(label="生成的音乐", show_label=False)
                    
                    song_output_info = gr.Markdown(value="等待生成...", elem_id="song-output-info")
                
            
            # 按钮事件绑定
            song_load_example_btn.click(
                fn=song_load_example,
                outputs=[song_lyrics]
            )
            
            song_format_btn.click(
                fn=song_format_lyrics,
                inputs=[song_lyrics],
                outputs=[song_lyrics]
            )
            
            song_btn.click(
                fn=song_generate,
                inputs=[song_lyrics, song_description, song_prompt_audio, song_auto_style,
                       song_gen_type, song_max_duration, song_cfg, song_temp,
                       song_top_k, song_top_p, song_low_mem],
                outputs=[song_output_audio, song_output_info]
            )
        
        # ==================== Avatar 页面 ====================
        with gr.Column(visible=False, elem_id="avatar-page") as avatar_page:
            with gr.Column(elem_id="avatar-header-container"):
                gr.HTML("""
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 20px 30px; 
                background: linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(0, 184, 148, 0.15) 100%);
                border-radius: 16px; margin-bottom: 25px; border: 1px solid rgba(0, 212, 170, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(0, 212, 170, 0.5));">🎼</span>
                        <div>
                            <h1 style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; 
                            background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%); 
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                            letter-spacing: 0.05em; margin: 0; font-weight: 800;">
                                歌韵织绘成影
                            </h1>
                            <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 5px 0 0 0; letter-spacing: 0.1em;">
                                LongCat-Video Avatar Engine
                            </p>
                        </div>
                    </div>
                </div>
                """)
                avatar_back_btn = gr.Button("↩️ 返回主页", size="sm", elem_id="avatar-back-btn")
            
            # Avatar 功能标签页
            with gr.Tabs() as avatar_function_tabs:
                
                # 单人说话视频
                with gr.TabItem("🎤 单人演唱视频生成", id="single_avatar"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            single_stage = gr.Radio(
                                ["ai2v", "at2v"], 
                                value="ai2v", 
                                label="生成模式",
                                info="ai2v: 图片+音频 | at2v: 文本+音频", elem_id="resolution-group"
                            )
                            single_audio = gr.Audio(
                                label="🎤 上传音频",
                                type="filepath"
                            )
                            single_image = gr.Image(
                                label="📷 参考图片 (ai2v 模式必需)",
                                type="filepath"
                            )
                            single_prompt = gr.Textbox(
                                label="场景描述",
                                placeholder="描述人物的场景和动作，建议包含 'speaking' 或 'talking'...",
                                lines=3,
                                value="A person is speaking in a professional studio with soft lighting."
                            )
                            
                            with gr.Accordion("⚙️ 高级参数", open=False):
                                single_resolution = gr.Radio(["480p", "720p"], value="480p", label="分辨率", elem_id="resolution-group")
                                with gr.Row():
                                    single_steps = gr.Slider(10, 100, value=50, step=1, label="推理步数")
                                    single_seed = gr.Number(value=42, label="随机种子")
                                with gr.Row():
                                    single_text_cfg = gr.Slider(1.0, 15.0, value=4.0, step=0.1, label="文本引导")
                                    single_audio_cfg = gr.Slider(1.0, 15.0, value=4.0, step=0.1, label="音频引导 (建议3-5)")
                                
                                gr.Markdown("**视频续写设置**")
                                single_segments = gr.Slider(1, 10, value=1, step=1, label="视频段数")
                                with gr.Row():
                                    single_ref_idx = gr.Slider(-10, 30, value=10, step=1, label="参考图索引 (0-24 更稳定)")
                                    single_mask_range = gr.Slider(1, 10, value=3, step=1, label="遮罩帧范围")
                            
                            single_btn = gr.Button("🎼生成单人视频", variant="primary", size="lg")
                        
                        with gr.Column(scale=1):
                            single_output_video = gr.Video(label="生成结果")
                            single_output_info = gr.Markdown(label="生成信息")
                
                # 双人对话视频
                with gr.TabItem("👥 双人对唱视频生成", id="multi_avatar"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            multi_image = gr.Image(
                                label="📷 参考图片 (包含两人)",
                                type="filepath"
                            )
                            with gr.Row():
                                multi_audio1 = gr.Audio(
                                    label="🎤 Person1 音频",
                                    type="filepath"
                                )
                                multi_audio2 = gr.Audio(
                                    label="🎤 Person2 音频",
                                    type="filepath"
                                )
                            
                            multi_audio_type = gr.Radio(
                                ["para", "add"],
                                value="para",
                                label="音频模式",
                                info="para: 并行(同时说话) | add: 顺序(轮流说话)", elem_id="audio-mode-radio"
                            )
                            
                            multi_prompt = gr.Textbox(
                                label="场景描述",
                                placeholder="描述两人对话的场景...",
                                lines=3,
                                value="Two people are having a conversation in a warmly lit room."
                            )
                            
                            with gr.Accordion("⚙️ 高级参数", open=False):
                                multi_resolution = gr.Radio(["480p", "720p"], value="480p", label="分辨率", elem_id="resolution-group")
                                with gr.Row():
                                    multi_steps = gr.Slider(10, 100, value=50, step=1, label="推理步数")
                                    multi_seed = gr.Number(value=42, label="随机种子")
                                with gr.Row():
                                    multi_text_cfg = gr.Slider(1.0, 15.0, value=4.0, step=0.1, label="文本引导")
                                    multi_audio_cfg = gr.Slider(1.0, 15.0, value=4.0, step=0.1, label="音频引导 (建议3-5)")
                                
                                gr.Markdown("**视频续写设置**")
                                multi_segments = gr.Slider(1, 10, value=1, step=1, label="视频段数")
                                with gr.Row():
                                    multi_ref_idx = gr.Slider(-10, 30, value=10, step=1, label="参考图索引")
                                    multi_mask_range = gr.Slider(1, 10, value=3, step=1, label="遮罩帧范围")
                                
                                gr.Markdown("**人物区域设置 (可选)**")
                                gr.Markdown("格式: y_min,x_min,y_max,x_max (留空则自动左右分割)")
                                with gr.Row():
                                    multi_bbox1 = gr.Textbox(label="Person1 区域", placeholder="100,80,800,640")
                                    multi_bbox2 = gr.Textbox(label="Person2 区域", placeholder="50,720,820,1300")
                            
                            multi_btn = gr.Button("🎼 生成双人视频", variant="primary", size="lg")
                        
                        with gr.Column(scale=1):
                            multi_output_video = gr.Video(label="生成结果")
                            multi_output_info = gr.Markdown(label="生成信息")
            
            # Avatar 按钮事件绑定
            single_btn.click(
                fn=avatar_single_generate,
                inputs=[single_audio, single_image, single_prompt, single_stage,
                       single_resolution, single_steps, single_text_cfg, single_audio_cfg,
                       single_seed, single_segments, single_ref_idx, single_mask_range],
                outputs=[single_output_video, single_output_info]
            )
            
            multi_btn.click(
                fn=avatar_multi_generate,
                inputs=[multi_image, multi_audio1, multi_audio2, multi_prompt,
                       multi_audio_type, multi_resolution, multi_steps, multi_text_cfg,
                       multi_audio_cfg, multi_seed, multi_segments, multi_ref_idx,
                       multi_mask_range, multi_bbox1, multi_bbox2],
                outputs=[multi_output_video, multi_output_info]
            )
            
        # ==================== 页面导航逻辑 ====================
        
        def show_video_page():
            return {
                home_page: gr.update(visible=False),
                video_page: gr.update(visible=True),
                song_page: gr.update(visible=False),
                avatar_page: gr.update(visible=False)
            }
        
        def show_song_page():
            return {
                home_page: gr.update(visible=False),
                video_page: gr.update(visible=False),
                song_page: gr.update(visible=True),
                avatar_page: gr.update(visible=False)
            }
        
        def show_avatar_page():
            return {
                home_page: gr.update(visible=False),
                video_page: gr.update(visible=False),
                song_page: gr.update(visible=False),
                avatar_page: gr.update(visible=True)
            }
        
        def show_home_page():
            return {
                home_page: gr.update(visible=True),
                video_page: gr.update(visible=False),
                song_page: gr.update(visible=False),
                avatar_page: gr.update(visible=False)
            }
        
        # 绑定导航事件
        video_enter_btn.click(
            fn=show_video_page,
            outputs=[home_page, video_page, song_page, avatar_page]
        )
        
        song_enter_btn.click(
            fn=show_song_page,
            outputs=[home_page, video_page, song_page, avatar_page]
        )
        
        avatar_enter_btn.click(
            fn=show_avatar_page,
            outputs=[home_page, video_page, song_page, avatar_page]
        )
        
        video_back_btn.click(
            fn=show_home_page,
            outputs=[home_page, video_page, song_page, avatar_page]
        )
        
        song_back_btn.click(
            fn=show_home_page,
            outputs=[home_page, video_page, song_page, avatar_page]
        )
        
        avatar_back_btn.click(
            fn=show_home_page,
            outputs=[home_page, video_page, song_page, avatar_page]
        )
        
        # ==================== 原关于标签页内容（已移除，改为主页展示）====================
        # 如果需要关于页面，可以在主页底部添加或创建单独页面
        
        if False:  # 保留原关于内容的代码，但不显示
            with gr.TabItem("ℹ️ 关于", id="about_tab"):
                gr.HTML("""
                <div style="max-width: 800px; margin: 0 auto; padding: 40px 20px;">
                    <div class="module-header">
                        <span class="feature-icon">🎭</span>
                        <h2 class="module-title">关于 Maestro</h2>
                    </div>
                    
                    <div style="background: rgba(15, 15, 25, 0.8); border-radius: 16px; padding: 30px; margin-top: 20px; border: 1px solid rgba(139, 92, 246, 0.3);">
                        <h3 style="color: #00f5ff; font-family: 'Orbitron', sans-serif; margin-bottom: 20px;">🎬 LongCat-Video</h3>
                        <p style="color: rgba(255,255,255,0.7); line-height: 1.8; margin-bottom: 20px;">
                            LongCat-Video 是一个强大的视频生成模型，支持多种生成模式：
                        </p>
                        <ul style="color: rgba(255,255,255,0.7); line-height: 2; padding-left: 20px;">
                            <li><strong>文本生成视频</strong> - 根据文本描述生成高质量视频</li>
                            <li><strong>图片生成视频</strong> - 让静态图片动起来</li>
                            <li><strong>音频驱动数字人</strong> - 根据音频生成说话的数字人</li>
                            <li><strong>视频延续</strong> - 延长现有视频的长度</li>
                        </ul>
                        
                        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent 0%, rgba(139, 92, 246, 0.5) 50%, transparent 100%); margin: 30px 0;">
                        
                        <h3 style="color: #ff00ff; font-family: 'Orbitron', sans-serif; margin-bottom: 20px;">🎵 SongGeneration</h3>
                        <p style="color: rgba(255,255,255,0.7); line-height: 1.8; margin-bottom: 20px;">
                            SongGeneration 是一个高质量的歌曲生成模型，能够：
                        </p>
                        <ul style="color: rgba(255,255,255,0.7); line-height: 2; padding-left: 20px;">
                            <li><strong>歌词生成歌曲</strong> - 根据歌词和风格描述生成完整歌曲</li>
                            <li><strong>人声+伴奏</strong> - 同时生成人声和伴奏，或分别生成</li>
                            <li><strong>多种风格</strong> - 支持 Pop, R&B, Rock, Jazz 等多种音乐风格</li>
                            <li><strong>风格迁移</strong> - 使用参考音频进行风格迁移</li>
                        </ul>
                        
                        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent 0%, rgba(139, 92, 246, 0.5) 50%, transparent 100%); margin: 30px 0;">
                        
                        <h3 style="color: #8b5cf6; font-family: 'Orbitron', sans-serif; margin-bottom: 20px;">📋 使用说明</h3>
                        <ol style="color: rgba(255,255,255,0.7); line-height: 2; padding-left: 20px;">
                            <li>确保已正确配置模型权重文件</li>
                            <li>选择所需的生成功能（视频或歌曲）</li>
                            <li>填写必要的输入参数</li>
                            <li>点击生成按钮开始创作</li>
                            <li>等待生成完成后查看/下载结果</li>
                        </ol>
                        
                        <div style="margin-top: 30px; padding: 20px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border-left: 4px solid #8b5cf6;">
                            <p style="color: rgba(255,255,255,0.8); margin: 0;">
                                <strong>💡 提示:</strong> 首次使用需要下载模型权重，请确保网络连接稳定并有足够的存储空间。
                            </p>
                        </div>
                    </div>
                </div>
                """)

        # ==================== 🆕 左下角悬浮菜单 HTML ====================
        gr.HTML("""
        <div class="settings-container">
            <div class="settings-menu">
                <div class="menu-header">
                    Maestro System v1.0
                </div>

                <a href="?view=api" target="_blank" class="menu-item">
                    <span>🔌</span> API 文档
                </a>

                <a href="https://gradio.app" target="_blank" class="menu-item">
                    <span>⚡</span> 构建技术 Gradio
                </a>

                <div class="menu-divider"></div>

                <div class="menu-item">
                    <span>⚙️</span> 系统设置
                </div>

                <div class="menu-item">
                    <span>🌗</span> 界面主题
                </div>
            </div>

            <div class="settings-btn">
                <span class="settings-icon">⚙️</span>
                <span>设置与帮助</span>
            </div>
        </div>
        """)

    return app


# ==================== 主入口 ====================

if __name__ == "__main__":
    app = create_app()
    # 核心修复：规范化项目根目录路径，确保盘符大写并统一使用正斜杠 
    # 这样能保证 Gradio 的沙箱校验字符串与请求字符串完全一致 
    abs_webui_dir = Path(WEBUI_DIR).resolve().as_posix() 
    
    app.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True,
        # 授权访问整个项目目录及其子目录 
        allowed_paths=[abs_webui_dir],
        js=get_rag_js_logic(),
        css=get_custom_css()
    )

