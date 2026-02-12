import os
import json
import random
from typing import TypedDict, List, Annotated, Sequence, Union, Literal
from pathlib import Path
import operator

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Load Knowledge Base
def load_kb(kb_path):
    try:
        if kb_path.exists():
            with open(kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"entries": []}
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return {"entries": []}

# Define State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str
    intent: str  # "greeting", "query", etc.
    final_response: str

class LangGraphRAG:
    def __init__(self, kb_path=None):
        if kb_path is None:
            kb_path = Path(__file__).parent.parent / "data" / "knowledge_base.json"
        
        # Setup API Key first
        self.api_key = os.environ.get("OPENAI_API_KEY", "sk-0baab104436548dbb8d62f4ce6c8c876")

        # 1. Setup Vector Store
        self.vector_store = self._build_vector_store(load_kb(kb_path))
        
        # 2. Setup LLM
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-max",
            temperature=0.7,
        )
        
        # 3. Bind Tools
        self.tools = [self.search_knowledge_base]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 4. Build Graph
        self.graph = self._build_graph()

    def _build_vector_store(self, kb_data):
        """Initialize FAISS vector store with knowledge base data."""
        docs = []
        for entry in kb_data.get("entries", []):
            # Combine content and keywords for semantic search
            text = f"{entry.get('content', '')} Keywords: {', '.join(entry.get('keywords', []))}"
            metadata = {
                "type": entry.get("type", "text"),
                "media_url": entry.get("media_url", ""),
                "keywords": entry.get("keywords", [])
            }
            docs.append(Document(page_content=text, metadata=metadata))
            
        if not docs:
            # Create a dummy doc if KB is empty to prevent errors
            docs = [Document(page_content="Empty Knowledge Base", metadata={"type": "text"})]

        # Use DashScope Embeddings (Alibaba)
        embeddings = DashScopeEmbeddings(
            model="text-embedding-v1",
            dashscope_api_key=os.environ.get("DASHSCOPE_API_KEY", self.api_key) # Try using same key
        )
        
        return FAISS.from_documents(docs, embeddings)

    @tool
    def search_knowledge_base(self, query: str):
        """
        Search the Northern Shaanxi culture knowledge base. 
        Use this tool when the user asks for specific information about folk songs, waist drums, paper cutting, food, etc.
        """
        # We need to access the instance 'self' inside the tool. 
        # Since @tool creates a static function, we'll wrap the logic or bind it properly.
        # But 'self' is not available in the static context.
        # So we define the tool logic separately and bind it in __init__ or use a closure.
        # Here, I'll use a trick: The instance method is bound when we create the tool list.
        pass # This is a placeholder for type hinting. Actual implementation is below.

    def _search_tool_impl(self, query: str):
        """Implementation of the search tool."""
        # print(f"\n[DEBUG] Tool 'search_knowledge_base' called with query: {query}")
        docs = self.vector_store.similarity_search(query, k=1)
        if not docs:
            # print("[DEBUG] No docs found in vector store.")
            return "No relevant information found."
        
        doc = docs[0]
        content = doc.page_content.split(" Keywords:")[0] # Remove appended keywords
        metadata = doc.metadata
        # print(f"[DEBUG] Found doc source: {metadata.get('source', 'unknown')} | Preview: {content[:50]}...")
        
        # Format return with metadata for the LLM to use
        media_url = metadata.get("media_url")
        
        if media_url:
            try:
                # 获取项目根目录（假设 langgraph_rag.py 在 modules/ 下） 
                project_root = Path(__file__).resolve().parent.parent
                # 拼接并生成绝对路径，强制转为正斜杠 Posix 格式 
                abs_path = (project_root / media_url.replace("\\", "/")).resolve()
                
                if abs_path.exists():
                    # 核心修复：Windows 下必须是 /file=E:/path 格式（无额外斜杠，盘符大写）
                    media_url = f"/file={abs_path.as_posix()}"
                else:
                    print(f"[Warning] File not found on disk: {abs_path}")
            except Exception as e:
                print(f"[Error] Path processing failed: {e}")

        result = {
            "content": content,
            "type": metadata.get("type"),
            "media_url": media_url
        }
        return json.dumps(result, ensure_ascii=False)

    def _build_graph(self):
        # Redefine the tool with access to self
        @tool("search_knowledge_base")
        def search_knowledge_base(query: str):
            """
            Search the Northern Shaanxi culture knowledge base. 
            Use this tool when the user asks for specific information about folk songs, waist drums, paper cutting, food, etc.
            """
            return self._search_tool_impl(query)

        self.tools = [search_knowledge_base]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("analyze_intent", self.analyze_intent)
        workflow.add_node("agent", self.agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("respond_greeting", self.respond_greeting)
        
        # Add Edges
        workflow.set_entry_point("analyze_intent")
        
        # Conditional Edge 1: Intent Analysis
        workflow.add_conditional_edges(
            "analyze_intent",
            self.route_intent,
            {
                "greeting": "respond_greeting",
                "query": "agent"
            }
        )
        
        # Conditional Edge 2: Agent Tool Usage
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", "agent")
        workflow.add_edge("respond_greeting", END)
        
        return workflow.compile()

    def analyze_intent(self, state: AgentState):
        """Analyze if the user input is a greeting or a query requiring knowledge."""
        query = state["messages"][-1].content
        
        # Simple rule-based classification to save tokens
        greetings_keywords = ["你好", "在吗", "hello", "hi", "早上好"]
        if any(query.lower().strip() == k for k in greetings_keywords) or len(query) < 2:
             return {"intent": "greeting", "query": query}
        
        return {"intent": "query", "query": query}

    def route_intent(self, state: AgentState):
        return state["intent"]

    def respond_greeting(self, state: AgentState):
        greetings = ["你好！我是陕北民歌 AI 助理。", "在呢，想了解点啥？", "咱们陕北文化博大精深，您可以问我关于信天游、秧歌或者剪纸的事儿。"]
        return {"final_response": random.choice(greetings)}

    def agent_node(self, state: AgentState):
        """The main agent node that calls LLM."""
        messages = state["messages"]
        
        # System Prompt
        system_prompt = """你是一个专业的陕北民歌文化 AI 助手，名字叫"陕北民歌助手"。
你的性格热情、豪爽，说话带有陕北特色。

**绝对禁令**：
- 严禁自己编造或猜测任何文件路径。
- 你必须【逐字逐句】使用 search_knowledge_base 工具返回结果中的 `media_url`。
- 如果工具返回的路径以 '/file=' 开头，你必须完整保留这个前缀，不要修改它。

**核心原则**：
1. **优先检索**：对于用户提出的任何关于陕北文化、民歌、习俗、节日、食物、特产、具体名词（如“信天游”、“腰鼓”）或“不知道”、“神秘”等相关的问题，你**必须**首先调用 `search_knowledge_base` 工具进行搜索，**绝对不要**仅凭记忆回答。
2. **多模态展示**：如果搜索结果包含 `media_url`，必须在回答末尾生成 Markdown 图片或音频链接。
3. **功能引导**：如果涉及视频生成、作曲、数字人，引导用户使用左侧功能模块。

**多模态生成规则**：
- 图片: 使用标准 Markdown 格式 `![Image](MEDIA_URL)`
- 音频: 使用标准 Markdown 格式 `[Audio](MEDIA_URL)`
"""
        # Ensure system prompt is the first message
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + list(messages)
        
        response = self.llm_with_tools.invoke(messages)
        
        # If response is final text (not tool call), set it as final_response
        if not response.tool_calls:
             return {"messages": [response], "final_response": response.content}
        
        return {"messages": [response]}

    def should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "continue"
        return "end"

    def run(self, query: str):
        """Run the graph."""
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "intent": "query", # default
            "final_response": ""
        }
        
        result = self.graph.invoke(initial_state)
        return result["final_response"]
