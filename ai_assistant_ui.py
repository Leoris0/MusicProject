
def get_ai_assistant_html():
    return """
    <div id="ai-assistant-root" class="ai-assistant-root">
        <!-- 悬浮球 -->
        <div id="ai-float-btn" class="ai-float-btn">
            <div class="ai-icon">
                <svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            </div>
            <div class="ai-text">AI 助手</div>
        </div>

        <!-- 聊天窗口 -->
        <div id="ai-chat-window" class="ai-chat-window hidden">
            <!-- 头部 -->
            <div class="ai-header">
                <div class="ai-header-left">
                    <span class="ai-header-title">陕北民歌 AI 助理</span>
                </div>
                <div class="ai-header-right">
                    <button class="ai-btn-icon" title="新对话">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
                    </button>
                    <button class="ai-btn-icon" title="历史记录">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    </button>
                    <button class="ai-btn-icon" title="全屏">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
                    </button>
                    <button class="ai-btn-icon" title="设置">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                    </button>
                    <button class="ai-btn-icon close-btn" title="关闭">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </div>
            </div>

            <!-- 内容区 -->
            <div class="ai-body" id="ai-body-content">
                <div class="ai-welcome-section">
                    <div class="ai-logo-large">
                        <svg viewBox="0 0 24 24" width="64" height="64" stroke="url(#grad1)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
                            <defs>
                                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#a855f7;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </div>
                    <h2 class="ai-welcome-text">你好，我是 <span class="highlight">陕北民歌</span> AI 助理</h2>
                    
                    <!-- 推荐卡片 -->
                    <div class="ai-cards-container">
                        <div class="ai-card" data-question="如何生成高质量视频？">
                            <div class="ai-card-icon">🎥</div>
                            <div class="ai-card-content">
                                <div class="ai-card-title">视频生成指南</div>
                                <div class="ai-card-desc">学习如何编写 Prompt</div>
                            </div>
                        </div>
                        <div class="ai-card" data-question="怎么制作数字人？">
                            <div class="ai-card-icon">👤</div>
                            <div class="ai-card-content">
                                <div class="ai-card-title">数字人教程</div>
                                <div class="ai-card-desc">音频驱动图片教程</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 消息列表 -->
                <div id="ai-messages-list" class="ai-messages-list"></div>
            </div>

            <!-- 底部输入区 -->
            <div class="ai-footer">
                <div class="ai-input-wrapper">
                    <textarea id="ai-user-input" placeholder="请输入您遇到的问题... (Shift+Enter 换行)" rows="1"></textarea>
                    <button class="ai-send-btn">
                        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    </button>
                </div>
                <div class="ai-footer-info">
                    内容由 AI 生成，仅供参考
                </div>
            </div>
        </div>
    </div>
    <style>
    /* 引入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');

    /* 悬浮球样式 */
    .ai-assistant-root {
        font-family: 'Noto Sans SC', 'Rajdhani', sans-serif;
        color: #fff;
    }
    
    .ai-float-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 64px;
        height: 64px;
        background: rgba(20, 20, 35, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 50%;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        cursor: pointer;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        border: 1px solid rgba(139, 92, 246, 0.3);
        overflow: hidden;
    }
    
    .ai-float-btn::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
        border-radius: 50%;
        z-index: -1;
    }

    .ai-float-btn:hover {
        transform: scale(1.1) translateY(-5px);
        box-shadow: 0 15px 40px rgba(139, 92, 246, 0.4);
        border-color: rgba(139, 92, 246, 0.6);
        background: rgba(20, 20, 35, 0.8);
    }
    
    .ai-float-btn .ai-icon {
        color: #a855f7;
        transition: transform 0.3s ease;
    }
    
    .ai-float-btn:hover .ai-icon {
        transform: scale(1.1) rotate(-10deg);
        color: #fff;
    }
    
    .ai-float-btn .ai-text {
        font-size: 10px;
        font-weight: 700;
        margin-top: 2px;
        background: linear-gradient(90deg, #a855f7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        transition: all 0.3s;
    }

    .ai-float-btn:hover .ai-text {
        background: #fff;
        -webkit-background-clip: unset;
        -webkit-text-fill-color: #fff;
    }
    
    /* 聊天窗口样式 */
    .ai-chat-window {
        position: fixed;
        bottom: 110px;
        right: 30px;
        width: 400px;
        height: 650px;
        max-height: 80vh;
        background: rgba(15, 15, 25, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.6),
            inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        opacity: 1;
        transform: translateY(0) scale(1);
        overflow: hidden;
        transform-origin: bottom right;
    }
    
    .ai-chat-window.hidden {
        opacity: 0;
        transform: translateY(40px) scale(0.9);
        pointer-events: none;
        visibility: hidden;
    }
    
    .ai-chat-window.fullscreen {
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        max-height: 100vh;
        bottom: auto;
        right: auto;
        border-radius: 0;
    }
    
    /* 头部 */
    .ai-header {
        padding: 18px 24px;
        background: rgba(255, 255, 255, 0.02);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(10px);
    }
    
    .ai-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* 删除头像和状态相关样式 */
    .ai-header-info {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    
    .ai-header-title {
        font-weight: 700;
        font-size: 1rem;
        color: #fff;
        letter-spacing: 0.5px;
    }
    
    .ai-header-right {
        display: flex;
        gap: 4px;
    }
    
    .ai-btn-icon {
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        padding: 6px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    
    .ai-btn-icon svg {
        width: 16px;
        height: 16px;
    }
    
    .ai-btn-icon:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
    }
    
    .ai-btn-icon.close-btn:hover {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }
    
    /* 内容区 */
    .ai-body {
        flex: 1;
        overflow-y: auto;
        padding: 24px;
        display: flex;
        flex-direction: column;
        scroll-behavior: smooth;
    }

    /* 滚动条美化 */
    .ai-body::-webkit-scrollbar {
        width: 4px;
    }
    .ai-body::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
    }
    
    .ai-welcome-section {
        text-align: center;
        margin-top: 40px;
        transition: opacity 0.3s;
    }
    
    .ai-logo-large {
        margin-bottom: 20px;
        display: inline-block;
        filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.3));
    }
    
    .ai-welcome-text {
        font-size: 1.4rem;
        margin-bottom: 40px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .ai-welcome-text .highlight {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    .ai-cards-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        padding: 0 10px 10px 10px;
    }
    
    .ai-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        cursor: pointer;
        text-align: left;
        transition: all 0.3s;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .ai-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(139, 92, 246, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }

    .ai-card-icon {
        font-size: 1.5rem;
    }
    
    .ai-card-title {
        font-weight: 600;
        color: #fff;
        margin-bottom: 4px;
        font-size: 0.9rem;
    }
    
    .ai-card-desc {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.75rem;
        line-height: 1.4;
    }
    
    /* 消息列表 */
    .ai-messages-list {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding-bottom: 10px;
    }
    
    .ai-message {
        max-width: 85%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 0.95rem;
        line-height: 1.6;
        position: relative;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .ai-message.user {
        align-self: flex-end;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: #fff;
        border-bottom-right-radius: 4px;
    }
    
    .ai-message.bot {
        align-self: flex-start;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        border-bottom-left-radius: 4px;
    }
    
    /* 底部 */
    .ai-footer {
        padding: 16px 24px 24px 24px;
        background: transparent;
    }
    
    .ai-input-wrapper {
        display: flex;
        gap: 12px;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 10px 16px;
        transition: all 0.3s;
        align-items: center;
    }
    
    .ai-input-wrapper:focus-within {
        border-color: #a855f7;
        background: rgba(0, 0, 0, 0.5);
        box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2);
    }
    
    #ai-user-input {
        flex: 1;
        background: transparent;
        border: none;
        color: #fff;
        resize: none;
        font-family: inherit;
        font-size: 0.95rem;
        max-height: 100px;
        outline: none;
        padding: 4px 0;
    }
    
    #ai-user-input::placeholder {
        color: rgba(255, 255, 255, 0.3);
    }
    
    .ai-send-btn {
        /* 关键修复：加入 !important 确保颜色生效 */
        background: #00f5ff !important;
        border: none !important;
        color: #000 !important;
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        width: 36px;
        height: 36px;
        flex-shrink: 0;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.5) !important;
    }

    /* 同时也给 SVG 设置颜色确保可见 */
    .ai-send-btn svg {
        color: #000 !important;
    }
    
    .ai-send-btn:hover {
        background: #fff;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
    }

    .ai-send-btn:disabled {
        background: #4b5563;
        cursor: not-allowed;
        box-shadow: none;
        opacity: 0.7;
    }
    
    .ai-footer-info {
        text-align: center;
        color: rgba(255, 255, 255, 0.2);
        font-size: 0.7rem;
        margin-top: 10px;
    }
    
    /* 隐藏 Gradio 后端交互组件 */
    #ai-hidden-input, #ai-hidden-output, #ai-hidden-btn, .force-hide {
        display: none !important;
        position: absolute;
        opacity: 0;
        z-index: -100;
        height: 0;
        width: 0;
        overflow: hidden;
    }
    </style>
    """

def get_ai_assistant_js():
    return """
    function initAiAssistant() {
        console.log("AI Assistant Init Triggered - Version 2.0 (RAG First)");
        
        // DOM 元素 ID
        const IDS = {
            FLOAT_BTN: 'ai-float-btn',
            CHAT_WINDOW: 'ai-chat-window',
            USER_INPUT: 'ai-user-input',
            MSG_LIST: 'ai-messages-list',
            BODY_CONTENT: 'ai-body-content',
            WELCOME: 'ai-welcome-section'
        };

        // 状态管理
        let isOpen = false;

        // 绑定事件处理器
        function bindEvents() {
            const floatBtn = document.getElementById(IDS.FLOAT_BTN);
            if (!floatBtn) return false;
            
            // 防止重复绑定 (通过检测自定义属性)
            if (floatBtn.getAttribute('data-initialized') === 'true') {
                return true;
            }

            console.log("Binding AI Assistant Events...");

            // 1. 悬浮球点击
            floatBtn.addEventListener('click', (e) => {
                console.log("Float btn clicked");
                e.preventDefault();
                e.stopPropagation();
                toggleAiChat();
            });

            // 2. 委托监听聊天窗口内部点击
            const chatWindow = document.getElementById(IDS.CHAT_WINDOW);
            if (chatWindow) {
                chatWindow.addEventListener('click', (e) => {
                    const target = e.target;
                    
                    const closeBtn = target.closest('.ai-btn-icon.close-btn');
                    const fullscreenBtn = target.closest('.ai-btn-icon[title="全屏"]');
                    const newChatBtn = target.closest('.ai-btn-icon[title="新对话"]');
                    const sendBtn = target.closest('.ai-send-btn');
                    const presetCard = target.closest('.ai-card');

                    if (closeBtn) {
                        toggleAiChat();
                        e.stopPropagation();
                    } else if (fullscreenBtn) {
                        toggleFullscreen();
                        e.stopPropagation();
                    } else if (newChatBtn) {
                        clearAiChat();
                        e.stopPropagation();
                    } else if (sendBtn) {
                        sendAiMessage();
                        e.stopPropagation();
                    } else if (presetCard) {
                        const question = presetCard.dataset.question;
                        if (question) {
                            const input = document.getElementById(IDS.USER_INPUT);
                            if (input) {
                                input.value = question;
                                sendAiMessage();
                            }
                        }
                        e.stopPropagation();
                    }
                });
            }

            // 3. 输入框回车监听
            const input = document.getElementById(IDS.USER_INPUT);
            if (input) {
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendAiMessage();
                    }
                });
            }
            
            // 4. 初始化后端监听
            setupBackendListener();

            // 标记已初始化
            floatBtn.setAttribute('data-initialized', 'true');
            return true;
        }

        // 监听后端返回 (通过 hidden output)
        function setupBackendListener() {
            const findOutput = setInterval(() => {
                // 对应修改：寻找 textarea 而不是 innerHTML
                const outputEl = document.querySelector('#ai-hidden-output textarea');
                if (outputEl) {
                    clearInterval(findOutput);
                    console.log("Backend Listener Setup (Textbox Mode)");
                    
                    const observer = new MutationObserver((mutations) => {
                        const typing = document.getElementById('ai-typing-indicator');
                        if (!typing) return;

                        // 关键修复：获取内容值，并判断是否包含 Gradio 的加载标识
                        const content = outputEl.value;
                        
                        // 逻辑：如果内容不为空，且不是初始态或加载态
                        if (content && content.trim().length > 0) {
                            hideTyping();
                            addAiMessage(content, 'bot');
                            enableInput();
                            // 清空隐藏输出框，防止下次误触
                            outputEl.value = "";
                            // 触发 input 事件以通知 Gradio (React/Svelte)
                            outputEl.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                    
                    observer.observe(outputEl, { attributes: true, attributeFilter: ['value'] });
                    
                    // 额外兼容：有些 Gradio 版本不触发属性变化，手动轮询值
                    setInterval(() => {
                        const typing = document.getElementById('ai-typing-indicator');
                        // 检查 value 是否有值
                        if (typing && outputEl.value && outputEl.value.trim() !== "") {
                             const content = outputEl.value;
                             hideTyping();
                             addAiMessage(content, 'bot');
                             enableInput();
                             outputEl.value = "";
                             outputEl.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }, 500);
                }
            }, 500);
        }

        // 轮询直到元素出现 (Gradio 动态渲染)
        const checkInterval = setInterval(() => {
            if (bindEvents()) {
                console.log("AI Assistant Events Bound Successfully");
                clearInterval(checkInterval);
            }
        }, 500);

        // 功能函数定义
        function toggleAiChat() {
            const win = document.getElementById(IDS.CHAT_WINDOW);
            if (!win) return;
            
            isOpen = !isOpen;
            if (isOpen) {
                win.classList.remove('hidden');
                setTimeout(() => document.getElementById(IDS.USER_INPUT)?.focus(), 100);
            } else {
                win.classList.add('hidden');
            }
        }

        function toggleFullscreen() {
            const win = document.getElementById(IDS.CHAT_WINDOW);
            if (!win) return;
            win.classList.toggle('fullscreen');
        }

        function clearAiChat() {
            const list = document.getElementById(IDS.MSG_LIST);
            if (list) list.innerHTML = '';
            const welcome = document.querySelector('.ai-welcome-section');
            if (welcome) welcome.style.display = 'block';
        }

        function sendAiMessage() {
            const input = document.getElementById(IDS.USER_INPUT);
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;

            // 禁用输入，防止重复发送
            disableInput();

            // UI 更新
            const welcome = document.querySelector('.ai-welcome-section');
            if (welcome) welcome.style.display = 'none';

            addAiMessage(text, 'user');
            input.value = '';
            
            showTyping();
            
            // 调用 Python 后端
            // Gradio 的 Textbox 输入框通常是 textarea
            // 我们尝试多种选择器以防万一
            const hiddenInput = document.querySelector('#ai-hidden-input textarea') || document.querySelector('#ai-hidden-input input');
            const hiddenBtn = document.getElementById('ai-hidden-btn');
            
            if (hiddenInput && hiddenBtn) {
                // React/Svelte 需要触发 input 事件
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                if (nativeInputValueSetter) {
                    nativeInputValueSetter.call(hiddenInput, text);
                } else {
                    hiddenInput.value = text;
                }
                hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                setTimeout(() => hiddenBtn.click(), 100);
            } else {
                console.error("Backend components not found");
                setTimeout(() => {
                    hideTyping();
                    addAiMessage("系统连接异常，请刷新页面。", 'bot');
                    enableInput(); // 恢复输入
                }, 1000);
            }
        }

        function disableInput() {
            const input = document.getElementById(IDS.USER_INPUT);
            const btn = document.querySelector('.ai-send-btn');
            if (input) input.disabled = true;
            if (btn) btn.disabled = true;
        }

        function enableInput() {
            const input = document.getElementById(IDS.USER_INPUT);
            const btn = document.querySelector('.ai-send-btn');
            if (input) {
                input.disabled = false;
                input.focus();
            }
            if (btn) btn.disabled = false;
        }

        function addAiMessage(text, type) {
            const list = document.getElementById(IDS.MSG_LIST);
            if (!list) return;
            
            const div = document.createElement('div');
            div.className = `ai-message ${type}`;
            
            let processed = text;
            
            // 1. 处理 Markdown 图片 (增强对 /file= 路径的支持) 
            processed = processed.replace(/!\[.*?\]\((.*?)\)/g, (match, url) => { 
                // 去除可能的引号或空白
                url = url.trim().replace(/^['"]|['"]$/g, '');
                return `<div class="ai-media-card"><img src="${url}" style="max-width: 100%; border-radius: 8px; margin-top: 10px;" onerror="console.error('Image load failed:', this.src)"></div>`; 
            }); 
            
            // 2. 处理 Markdown 音频 (增强对 /file= 路径的支持)
            processed = processed.replace(/\[.*?\]\((.*?)\)/g, (match, url) => { 
                url = url.trim().replace(/^['"]|['"]$/g, '');
                // 只要是 /file= 开头，或者是常见的音频格式，都渲染为播放器
                if (url.includes('/file=') || /\.(mp3|wav|ogg|flac|aac)/i.test(url)) { 
                    return `<div class="ai-media-card"><audio controls src="${url}" style="width: 100%; margin-top: 10px;"></audio></div>`; 
                } 
                return match; 
            }); 

            // 3. 处理加粗 
            processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

            div.innerHTML = processed; 
            list.appendChild(div);
            
            const body = document.getElementById(IDS.BODY_CONTENT);
            if (body) body.scrollTop = body.scrollHeight;
        }

        function showTyping() {
            const list = document.getElementById(IDS.MSG_LIST);
            if (!list) return;
            const div = document.createElement('div');
            div.id = 'ai-typing-indicator';
            div.className = 'ai-message bot';
            div.innerText = '正在思考...';
            list.appendChild(div);
            const body = document.getElementById(IDS.BODY_CONTENT);
            if (body) body.scrollTop = body.scrollHeight;
        }

        function hideTyping() {
            const div = document.getElementById('ai-typing-indicator');
            if (div) div.remove();
        }

        // getAiReply 已移除，由 Python 后端接管
    }
    initAiAssistant();
    """
