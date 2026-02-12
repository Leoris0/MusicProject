
import json
import os
from pathlib import Path
import re
import random
import requests
import gradio as gr
from ai_assistant_ui import get_ai_assistant_html, get_ai_assistant_js
from modules.langgraph_rag import LangGraphRAG

# Singleton instance
rag_assistant = LangGraphRAG()

def get_rag_response(query):
    return rag_assistant.run(query)

def create_rag_interface():
    """
    创建 AI 助手的 RAG 接口组件。
    包含 HTML 结构注入和隐藏的 JS-Python 通信组件。
    应在 gr.Blocks 上下文中调用。
    """
    # 注入 AI 助手 UI
    gr.HTML(get_ai_assistant_html())

    # AI 助手后台交互组件 (隐藏)
    # 将 HTML 改为 Textbox，并保持隐藏
    ai_hidden_input = gr.Textbox(visible=True, elem_id="ai-hidden-input", elem_classes=["force-hide"])
    # 关键点：改为 Textbox
    ai_hidden_output = gr.Textbox(visible=True, elem_id="ai-hidden-output", elem_classes=["force-hide"])
    ai_hidden_btn = gr.Button(visible=True, elem_id="ai-hidden-btn", elem_classes=["force-hide"])

    ai_hidden_btn.click(
        fn=get_rag_response,
        inputs=[ai_hidden_input],
        outputs=[ai_hidden_output]
    )

def get_rag_js_logic():
    """获取 AI 助手的 JS 逻辑代码"""
    return get_ai_assistant_js()
