# """Streamlit ChatGPT-style frontend tailored for coding workflows."""

# import re
# from typing import Any, Dict, List

# import streamlit as st


# CHAT_MODES = ["Generate Code", "Explain Code"]
# MODEL_OPTIONS = ["gpt-5-mini", "gpt-5-mini-code", "custom-model"]
# DEFAULT_SYSTEM_PROMPT = "You are a senior AI pair programmer who writes and explains clean code."
# CODE_BLOCK_PATTERN = re.compile(r"```(?P<lang>[\w+\-]*)\n(?P<code>.*?)```", re.DOTALL)



# def create_persistent_chat(title: str = "New chat") -> str:
#     """Create a saved conversation and return its identifier."""
#     chat_id = str(st.session_state.chat_counter)
#     st.session_state.chat_counter += 1
#     st.session_state.chats[chat_id] = {"title": title, "messages": []}
#     return chat_id


# def ensure_current_chat() -> None:
#     """Make sure we have at least one persistent chat selected."""
#     if not st.session_state.chats:
#         chat_id = create_persistent_chat()
#         st.session_state.current_chat_id = chat_id
#     elif st.session_state.current_chat_id not in st.session_state.chats:
#         st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))


# def init_session_state() -> None:
#     """Bootstrap all keys required by the UI."""
#     st.session_state.setdefault("chat_counter", 1)
#     st.session_state.setdefault("chats", {})
#     st.session_state.setdefault("current_chat_id", "")
#     st.session_state.setdefault("is_temp_chat", False)
#     st.session_state.setdefault("temp_messages", [])
#     st.session_state.setdefault("display_name", "Developer")
#     st.session_state.setdefault("mode_select", CHAT_MODES[0])
#     st.session_state.setdefault("model_select", MODEL_OPTIONS[0])
#     st.session_state.setdefault("system_prompt_area", DEFAULT_SYSTEM_PROMPT)
#     st.session_state.setdefault("show_search_box", False)
#     st.session_state.setdefault("chat_search", "")
#     st.session_state.setdefault("sidebar_notice", "")

#     ensure_current_chat()


# def inject_custom_css() -> None:
#     """Inject a lightweight dark theme + sidebar styling to mimic ChatGPT."""
#     st.markdown(
#         """
#         <style>
#         :root { color-scheme: dark; }
#         body, .stApp, .block-container {
#             background-color: #050509;
#             color: #f5f7ff;
#         }
#         .block-container {
#             padding-top: 2.5rem;
#             padding-bottom: 5rem;
#             max-width: 900px;
#         }
#         div[data-testid="stSidebar"] {
#             background-color: #0c0f1a;
#             border-right: 1px solid #191d2d;
#         }
#         div[data-testid="stSidebar"] * {
#             color: #e0e6ff !important;
#         }
#         .sidebar-logo {
#             font-size: 1.05rem;
#             letter-spacing: 0.08em;
#             text-transform: uppercase;
#             font-weight: 600;
#             display: flex;
#             align-items: center;
#             gap: 0.4rem;
#             margin-bottom: 1rem;
#         }
#         .sidebar-nav {
#             display: flex;
#             flex-direction: column;
#             gap: 0.35rem;
#             margin: 1rem 0 1.4rem 0;
#         }
#         .sidebar-nav-item {
#             display: flex;
#             align-items: center;
#             gap: 0.55rem;
#             padding: 0.45rem 0.75rem;
#             border-radius: 12px;
#             border: 1px solid rgba(255,255,255,0.05);
#             background: rgba(255,255,255,0.02);
#             font-size: 0.9rem;
#         }
#         .sidebar-section-title {
#             text-transform: uppercase;
#             font-size: 0.75rem;
#             letter-spacing: 0.14em;
#             color: #8f96c2;
#             margin-bottom: 0.4rem;
#         }
#         .shortcut-btn button,
#         .shortcut-row button {
#             width: 100%;
#             border-radius: 12px;
#             border: 1px solid rgba(255,255,255,0.05);
#             background: rgba(255,255,255,0.02);
#             font-size: 0.9rem;
#             padding: 0.45rem 0.6rem;
#         }
#         .shortcut-row button {
#             font-size: 0.85rem;
#             padding: 0.35rem 0.45rem;
#         }
#         .gpt-pill-row {
#             display: flex;
#             gap: 0.5rem;
#         }
#         .gpt-pill {
#             padding: 0.35rem 0.85rem;
#             border-radius: 999px;
#             border: 1px solid #2f3547;
#             font-size: 0.85rem;
#             color: #dfe4ff;
#             background: rgba(255,255,255,0.04);
#         }
#         .chat-item-radio div[role="radiogroup"] > div {
#             background: rgba(255,255,255,0.02);
#             border: 1px solid rgba(255,255,255,0.05);
#             padding: 0.4rem 0.6rem;
#             border-radius: 12px;
#             margin-bottom: 0.35rem;
#         }
#         .chat-item-radio label {
#             width: 100%;
#         }
#         .chat-item-radio div[role="radiogroup"] input:checked + div {
#             border-color: #7a83ff;
#             background: rgba(122,131,255,0.08);
#         }
#         div[data-testid="stChatMessage"] {
#             margin-bottom: 1.2rem;
#         }
#         .chat-bubble {
#             width: 100%;
#             border-radius: 18px;
#             border: 1px solid #1f2335;
#             padding: 1rem 1.25rem;
#             margin-top: 0.25rem;
#             box-shadow: 0 0 40px rgba(4, 6, 15, 0.65);
#             background: #0e1425;
#         }
#         .assistant-bubble { background: linear-gradient(145deg, #10182d, #0b0f1a); }
#         .user-bubble { background: linear-gradient(145deg, #1c2339, #13192b); }
#         .hero-card {
#             text-align: center;
#             margin: 6rem auto 4rem auto;
#             padding: 4rem 2rem;
#             max-width: 680px;
#         }
#         .hero-pill {
#             display: inline-flex;
#             border: 1px solid #2f3244;
#             border-radius: 999px;
#             padding: 0.15rem 0.9rem;
#             font-size: 0.9rem;
#             letter-spacing: 0.08em;
#             text-transform: uppercase;
#             color: #9ea3c7;
#             margin-bottom: 1rem;
#         }
#         .hero-title {
#             font-size: clamp(2.5rem, 5vw, 3.6rem);
#             font-weight: 600;
#             color: #f9fbff;
#             margin-bottom: 0.6rem;
#         }
#         .hero-subtitle { color: #99a1c7; font-size: 1.2rem; }
#         div[data-testid="stChatInput"] > div {
#             border: 1px solid #20283d;
#             border-radius: 22px;
#             background: #0d1322;
#             padding: 0.4rem 0.6rem;
#             box-shadow: 0 10px 45px rgba(5, 8, 20, 0.45);
#         }
#         div[data-testid="stChatInput"] textarea {
#             background: transparent !important;
#             color: #f5f7ff !important;
#         }
#         div[data-testid="stSidebar"] button {
#             border-radius: 16px;
#             border: 1px solid #2f3547;
#             background: #161c2e;
#         }
#         div[data-testid="stSidebar"] button:hover {
#             border-color: #6b72ff;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )


# def set_sidebar_notice(message: str) -> None:
#     """Store a short notice message for sidebar alerts."""
#     st.session_state.sidebar_notice = message


# def get_active_messages() -> List[Dict[str, Any]]:
#     """Return the list that represents the active conversation."""
#     if st.session_state.is_temp_chat:
#         return st.session_state.temp_messages
#     return st.session_state.chats[st.session_state.current_chat_id]["messages"]


# def parse_and_render_segments(content: str) -> None:
#     """Render Markdown text mixed with fenced code blocks."""
#     start = 0
#     for match in CODE_BLOCK_PATTERN.finditer(content):
#         text_chunk = content[start : match.start()].strip()
#         if text_chunk:
#             st.markdown(text_chunk)

#         language = match.group("lang") or "text"
#         st.code(match.group("code"), language=language.strip())
#         start = match.end()

#     tail = content[start:].strip()
#     if tail:
#         st.markdown(tail)


# def render_chat_history(messages: List[Dict[str, Any]]) -> None:
#     """Loop through session messages and display them with avatars and bubbles."""
#     for message in messages:
#         role = message.get("role", "assistant")
#         avatar = "🧑" if role == "user" else "🤖"
#         with st.chat_message(role, avatar=avatar):
#             bubble_class = "user-bubble" if role == "user" else "assistant-bubble"
#             st.markdown(f"<div class='chat-bubble {bubble_class}'>", unsafe_allow_html=True)
#             parse_and_render_segments(message.get("content", ""))
#             st.markdown("</div>", unsafe_allow_html=True)


# def render_empty_state(display_name: str) -> None:
#     """Hero section that mirrors ChatGPT's welcome card when chat is empty."""
#     st.markdown(
#         f"""
#         <div class="hero-card">
#             <div class="hero-pill">CODE GEN AI</div>
#             <div class="hero-title">Hey, {display_name}. Ready to dive in?</div>
#             <div class="hero-subtitle">Ask anything about code — generation, debugging, or explanation.</div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


# def clear_conversation() -> None:
#     """Clear only the currently active conversation."""
#     messages = get_active_messages()
#     messages.clear()


# def summarize_title(prompt: str) -> str:
#     """Generate a short title from the first user message."""
#     condensed = prompt.strip().splitlines()[0][:36]
#     return condensed + ("…" if len(prompt.strip()) > len(condensed) else "") or "New chat"


# def send_to_backend(
#     messages: List[Dict[str, Any]],
#     *,
#     mode: str,
#     system_prompt: str,
#     model: str,
# ) -> str:
#     """Stub that simulates an assistant reply."""
#     user_prompt = next(
#         (msg.get("content", "") for msg in reversed(messages) if msg.get("role") == "user"),
#         "",
#     )

#     if not user_prompt:
#         return "I'm ready whenever you are. Ask me something about code!"

#     if mode == "Generate Code":
#         return (
#             "Here's a quick scaffold inspired by your request. Customize or expand it once you plug in "
#             "your Ollama backend.\n\n"
#             "```python\n"
#             "def generated_solution(*args, **kwargs):\n"
#             "    \"\"\"Auto-generated stub based on your latest prompt.\"\"\"\n"
#             "    # TODO: replace with the logic you need\n"
#             "    raise NotImplementedError('Hook this up to your Ollama call')\n"
#             "```\n\n"
#             "**What to do next**\n"
#             "1. Replace this stub with code streamed from your model.\n"
#             "2. Use the system prompt to enforce style or testing preferences.\n"
#             f"3. Model selector currently reads `{model}` for you to map to a real deployment."
#         )

#     if mode == "Explain Code":
#         summary = (
#             "I scanned the snippet you shared and prepared a concise explanation. "
#             "Swap this out with a real analysis response once Ollama is wired up."
#         )
#         bullets = (
#             "- **What it does:** Parses your input, performs the described transformation, and returns the result.\n"
#             "- **Key considerations:** Consider adding docstrings, logging, and unit tests.\n"
#             "- **Complexity:** Roughly O(n) with respect to the input size.\n"
#         )
#         return f"{summary}\n\n{bullets}\n\nLet me know if you want a refactor or test suite."

#     return (
#         "Frontend is live! Pick a mode in the sidebar or wire `send_to_backend` to Ollama "
#         "for real responses."
#     )


# def handle_user_prompt(user_prompt: str, mode: str, system_prompt: str, model: str) -> None:
#     """Persist the new user prompt, get assistant reply, and re-render."""
#     messages = get_active_messages()
#     messages.append({"role": "user", "content": user_prompt})
#     assistant_reply = send_to_backend(
#         messages,
#         mode=mode,
#         system_prompt=system_prompt,
#         model=model,
#     )
#     messages.append({"role": "assistant", "content": assistant_reply})

#     if not st.session_state.is_temp_chat:
#         chat_meta = st.session_state.chats[st.session_state.current_chat_id]
#         if chat_meta["title"] == "New chat" and user_prompt.strip():
#             chat_meta["title"] = summarize_title(user_prompt)


# def start_new_chat() -> None:
#     """Start a fresh conversation respecting the temp toggle."""
#     if st.session_state.is_temp_chat:
#         st.session_state.temp_messages = []
#     else:
#         chat_id = create_persistent_chat()
#         st.session_state.current_chat_id = chat_id


# def render_chat_list() -> None:
#     """Renderable list of saved chats similar to ChatGPT sidebar."""
#     if not st.session_state.chats:
#         st.caption("No saved chats yet. Start typing to create one.")
#         return

#     chat_ids = list(st.session_state.chats.keys())
#     query = st.session_state.chat_search.strip().lower()
#     if query:
#         chat_ids = [cid for cid in chat_ids if query in st.session_state.chats[cid]["title"].lower()]
#         if not chat_ids:
#             st.caption("No chats match your search.")
#             return

#     current_id = st.session_state.current_chat_id
#     if current_id not in chat_ids:
#         current_id = chat_ids[0]
#         st.session_state.current_chat_id = current_id

#     index = chat_ids.index(current_id)
#     selection = st.radio(
#         "Your chats",
#         options=chat_ids,
#         index=index,
#         format_func=lambda cid: st.session_state.chats[cid]["title"],
#         label_visibility="collapsed",
#         key="chat_history_selector",
#     )
#     if selection != current_id:
#         st.session_state.current_chat_id = selection


# def render_sidebar() -> tuple[str, str, str]:
#     """Full sidebar layout including nav, GPTs, chats, and assistant controls."""
#     with st.sidebar:
#         st.markdown('<div class="sidebar-logo">⚪ CODE GEN AI</div>', unsafe_allow_html=True)
#         if st.button("＋ New chat", use_container_width=True):
#             start_new_chat()

#         st.markdown('<div class="sidebar-section-title">Shortcuts</div>', unsafe_allow_html=True)
#         if st.button("🔍 Search chats", key="nav_search", use_container_width=True):
#             st.session_state.show_search_box = not st.session_state.show_search_box
#             if not st.session_state.show_search_box:
#                 st.session_state.chat_search = ""

#         if st.session_state.show_search_box:
#             st.text_input(
#                 "Search your conversations",
#                 key="chat_search",
#                 placeholder="Type to filter chat titles",
#             )

#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("📚 Library", key="nav_library", use_container_width=True):
#                 set_sidebar_notice("Library is a placeholder — connect docs or snippets later.")
#         with col2:
#             if st.button("🗂️ Projects", key="nav_projects", use_container_width=True):
#                 set_sidebar_notice("Projects hub coming soon. Map repos or tasks here.")

#         if st.session_state.sidebar_notice:
#             st.info(st.session_state.sidebar_notice)
#             if st.button("Dismiss", key="nav_dismiss", use_container_width=True):
#                 st.session_state.sidebar_notice = ""

#         temp_toggle = st.toggle(
#             "Temporary chat",
#             value=st.session_state.is_temp_chat,
#             help="When enabled, chats are not saved to history.",
#         )
#         if temp_toggle != st.session_state.is_temp_chat:
#             st.session_state.is_temp_chat = temp_toggle
#             if temp_toggle:
#                 st.session_state.temp_messages = []
#             else:
#                 ensure_current_chat()

#         if st.session_state.is_temp_chat:
#             st.caption("Temporary chat is on. Nothing will show up under 'Your chats'.")
#         else:
#             st.markdown('<div class="sidebar-section-title">Your chats</div>', unsafe_allow_html=True)
#             with st.container():
#                 st.markdown('<div class="chat-item-radio">', unsafe_allow_html=True)
#                 render_chat_list()
#                 st.markdown('</div>', unsafe_allow_html=True)

          
#         st.markdown("---")
#         st.subheader("Assistant Controls")
#         display_name = st.text_input("Display name", value=st.session_state.display_name)
#         st.session_state.display_name = display_name or "Developer"

#         mode = st.selectbox("Mode", options=CHAT_MODES, key="mode_select")
#         model = st.selectbox("Model (placeholder)", options=MODEL_OPTIONS, key="model_select")
#         system_prompt = st.text_area(
#             "System prompt",
#             value=DEFAULT_SYSTEM_PROMPT,
#             height=120,
#             key="system_prompt_area",
#         )

#         if st.button("Clear conversation", use_container_width=True):
#             clear_conversation()
#             st.rerun()

#         st.caption("Backend stub: edit `send_to_backend` in FrontEnd.py to call Ollama/OpenAI.")

#     return mode, model, system_prompt


# def main() -> None:
#     st.set_page_config(page_title="ChatGPT-style Code Companion", layout="wide")
#     inject_custom_css()
#     init_session_state()

#     # Simplified UI: no sidebar. Display a small header and the hero/home content.
#     st.markdown('<div class="sidebar-logo">⚪ CODE GEN AI</div>', unsafe_allow_html=True)

#     # Use default mode/model/system_prompt values (sidebar removed)
#     mode = CHAT_MODES[0]
#     model = MODEL_OPTIONS[0]
#     system_prompt = st.session_state.get("system_prompt_area", DEFAULT_SYSTEM_PROMPT)

#     messages = get_active_messages()

#     if messages:
#         render_chat_history(messages)
#     else:
#         render_empty_state(st.session_state.display_name)

#     # Single prompt input for the simplified frontend
#     user_prompt = st.chat_input("Ask anything about your code — generation, debugging, or explanation...")
#     if user_prompt:
#         handle_user_prompt(user_prompt.strip(), mode, system_prompt.strip(), model)
#         st.rerun()


# if __name__ == "__main__":
#     main()


import streamlit as st
import requests
import json
from json import JSONDecodeError
from openai import OpenAI
import base64
from datetime import datetime
import uuid
from PIL import Image
import io

# Configuration
API_URL = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}
MODEL_OPTIONS = ["gpt-oss-120b", "llama3", "deepseek-r1"]

# Page config
st.set_page_config(
    page_title="Code Gen AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #3d3d5c;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #1e3a5f;
        border-left: 4px solid #667eea;
    }
    .assistant-message {
        background-color: #2d2d44;
        border-left: 4px solid #764ba2;
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 1rem;
    }
    .chat-item {
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .chat-item:hover {
        background-color: #3d3d5c;
    }
    .stButton > button {
        width: 100%;
    }
    div[data-testid="stCodeBlock"] {
        background-color: #1e1e2e;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_temporary" not in st.session_state:
        st.session_state.is_temporary = False
    if "selected_chats" not in st.session_state:
        st.session_state.selected_chats = set()
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "feature_mode" not in st.session_state:
        st.session_state.feature_mode = "Code Generation"


init_session_state()


# Helper functions
def generate_chat_id():
    return str(uuid.uuid4())[:8]


def create_new_chat(is_temporary=False):
    chat_id = generate_chat_id()
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    st.session_state.is_temporary = is_temporary
    
    if not is_temporary:
        st.session_state.chats[chat_id] = {
            "id": chat_id,
            "title": "New Chat",
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "feature_mode": st.session_state.feature_mode
        }
    return chat_id


def save_current_chat():
    if st.session_state.current_chat_id and not st.session_state.is_temporary:
        if st.session_state.current_chat_id in st.session_state.chats:
            st.session_state.chats[st.session_state.current_chat_id]["messages"] = st.session_state.messages
            # Update title based on first user message
            if st.session_state.messages:
                first_msg = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), None)
                if first_msg:
                    st.session_state.chats[st.session_state.current_chat_id]["title"] = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg


def load_chat(chat_id):
    if chat_id in st.session_state.chats:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chats[chat_id]["messages"].copy()
        st.session_state.is_temporary = False
        st.session_state.feature_mode = st.session_state.chats[chat_id].get("feature_mode", "Code Generation")


def delete_selected_chats():
    for chat_id in st.session_state.selected_chats:
        if chat_id in st.session_state.chats:
            del st.session_state.chats[chat_id]
    st.session_state.selected_chats = set()
    if st.session_state.current_chat_id in st.session_state.selected_chats:
        st.session_state.current_chat_id = None
        st.session_state.messages = []


def clear_current_chat():
    st.session_state.messages = []
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
        st.session_state.chats[st.session_state.current_chat_id]["messages"] = []


def filter_chats(query):
    if not query:
        return st.session_state.chats
    return {
        k: v for k, v in st.session_state.chats.items()
        if query.lower() in v["title"].lower()
    }


def stream_generate_ollama(model: str, prompt: str):
    """Stream response from Ollama API"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    try:
        with requests.post(API_URL, headers=HEADERS, json=payload, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                    
                line = raw_line.strip()
                try:
                    obj = json.loads(line)
                except JSONDecodeError:
                    continue
                
                chunk_text = None
                if "message" in obj and isinstance(obj["message"], dict):
                    chunk_text = obj["message"].get("content")
                elif "response" in obj:
                    chunk_text = obj.get("response")
                
                if chunk_text:
                    yield chunk_text
                
                if obj.get("done") is True:
                    break
    except requests.exceptions.RequestException as e:
        yield f"Error connecting to Ollama: {str(e)}"


def stream_generate_groq(prompt: str):
    """Stream response from Groq API"""
    try:
        client = OpenAI(
            api_key="key",  # Replace with your actual API key
            base_url="https://api.groq.com/openai/v1",
        )
        
        response = client.responses.create(
            input=prompt,
            model="openai/gpt-oss-120b",
            stream=True
        )
        
        for event in response:
            if hasattr(event, "delta"):
                delta = event.delta
                if hasattr(delta, "text") and delta.text:
                    yield delta.text
                elif isinstance(delta, str):
                    yield delta
            elif isinstance(event, str):
                yield event
                
    except Exception as e:
        yield f"Error connecting to Groq API: {str(e)}"


def generate_response(prompt: str, model: str, feature_mode: str):
    """Generate AI response based on the selected model and feature"""
    # Enhance prompt based on feature mode
    if feature_mode == "Code Generation":
        enhanced_prompt = f"""You are an expert code generator. Generate clean, well-documented, and efficient code based on the following request. Include comments explaining the code.

Request: {prompt}

Please provide the code with proper formatting and explanations."""
    else:  # Code Explanation
        enhanced_prompt = f"""You are an expert code explainer. Analyze and explain the following code in detail. Break down the logic, explain what each part does, and highlight any important concepts or patterns used.

Code/Question: {prompt}

Please provide a comprehensive explanation."""

    if model == "gpt-oss-120b":
        return stream_generate_groq(enhanced_prompt)
    else:
        return stream_generate_ollama(model, enhanced_prompt)


def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-title">🤖 Code Gen AI</p>', unsafe_allow_html=True)
    
    # New Chat buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            create_new_chat(is_temporary=False)
            st.rerun()
    with col2:
        if st.button("⏱️ Temp Chat", use_container_width=True, help="Create a temporary chat that won't be saved"):
            create_new_chat(is_temporary=True)
            st.rerun()
    
    st.divider()
    
    # Search chats
    st.markdown("**🔍 Search Chats**")
    search_query = st.text_input("Search...", value=st.session_state.search_query, label_visibility="collapsed", placeholder="Search chats...")
    st.session_state.search_query = search_query
    
    st.divider()
    
    # Chat management buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Delete Selected", use_container_width=True, disabled=len(st.session_state.selected_chats) == 0):
            delete_selected_chats()
            st.rerun()
    with col2:
        if st.button("🧹 Clear Chat", use_container_width=True):
            clear_current_chat()
            st.rerun()
    
    st.divider()
    
    # Previous chats list
    st.markdown("**📜 Previous Chats**")
    
    filtered_chats = filter_chats(search_query)
    
    if filtered_chats:
        for chat_id, chat_data in sorted(filtered_chats.items(), key=lambda x: x[1]["created_at"], reverse=True):
            col1, col2 = st.columns([0.15, 0.85])
            
            with col1:
                is_selected = chat_id in st.session_state.selected_chats
                if st.checkbox("", value=is_selected, key=f"select_{chat_id}", label_visibility="collapsed"):
                    st.session_state.selected_chats.add(chat_id)
                else:
                    st.session_state.selected_chats.discard(chat_id)
            
            with col2:
                is_current = chat_id == st.session_state.current_chat_id
                button_type = "primary" if is_current else "secondary"
                feature_icon = "⚡" if chat_data.get("feature_mode") == "Code Generation" else "📖"
                
                if st.button(
                    f"{feature_icon} {chat_data['title'][:25]}...",
                    key=f"chat_{chat_id}",
                    use_container_width=True,
                    type=button_type
                ):
                    save_current_chat()
                    load_chat(chat_id)
                    st.rerun()
    else:
        st.info("No chats yet. Start a new conversation!")
    
    # Temporary chat indicator
    if st.session_state.is_temporary:
        st.divider()
        st.warning("⏱️ Temporary chat mode - This chat won't be saved")


# Main content area
st.markdown('<h1 class="main-header">🤖 Code Gen AI</h1>', unsafe_allow_html=True)

# Feature selection and model selection
col1, col2 = st.columns(2)

with col1:
    feature_mode = st.selectbox(
        "🎯 Select Feature",
        ["Code Generation", "Code Explanation"],
        index=0 if st.session_state.feature_mode == "Code Generation" else 1,
        help="Choose between generating new code or explaining existing code"
    )
    st.session_state.feature_mode = feature_mode

with col2:
    selected_model = st.selectbox(
        "🧠 Select Model",
        MODEL_OPTIONS,
        help="Choose the AI model for generation"
    )

# Feature description
if feature_mode == "Code Generation":
    st.info("⚡ **Code Generation Mode**: Describe what you want to build, and AI will generate the code for you.")
else:
    st.info("📖 **Code Explanation Mode**: Paste your code or ask questions about code, and AI will explain it in detail.")

st.divider()

# Input methods tabs
st.markdown("### 📥 Input Methods")
input_tab1, input_tab2, input_tab3 = st.tabs(["💬 Text Input", "🖼️ Image Input", "🎤 Voice Input"])

user_input = None
image_context = None

with input_tab1:
    if feature_mode == "Code Generation":
        text_input = st.text_area(
            "Enter your prompt",
            placeholder="Describe the code you want to generate...\n\nExample: Create a Python function that calculates the Fibonacci sequence",
            height=150,
            label_visibility="collapsed"
        )
    else:
        text_input = st.text_area(
            "Enter code or question",
            placeholder="Paste code to explain or ask a question about code...\n\nExample: Explain how this sorting algorithm works...",
            height=150,
            label_visibility="collapsed"
        )
    
    if st.button("🚀 Submit Text", use_container_width=True, type="primary"):
        if text_input.strip():
            user_input = text_input

with input_tab2:
    uploaded_image = st.file_uploader(
        "Upload an image of code or diagram",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        help="Upload a screenshot of code or a diagram to analyze"
    )
    
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        image_description = st.text_input(
            "Add context about the image (optional)",
            placeholder="Describe what you want to know about this image..."
        )
        
        if st.button("🚀 Analyze Image", use_container_width=True, type="primary"):
            image_context = image_to_base64(image)
            if feature_mode == "Code Generation":
                user_input = f"[Image uploaded] {image_description if image_description else 'Generate code based on this image/diagram'}"
            else:
                user_input = f"[Image uploaded] {image_description if image_description else 'Explain the code shown in this image'}"

with input_tab3:
    st.markdown("""
    **🎤 Voice Input Instructions:**
    
    1. Click the microphone button below to start recording
    2. Speak your prompt clearly
    3. Click stop when finished
    4. Your speech will be transcribed and submitted
    """)
    
    # Note: Streamlit doesn't have native voice input, so we provide alternative
    st.warning("⚠️ Voice input requires browser microphone access. Use the Web Speech API integration below.")
    
    # HTML/JS for voice input
    voice_input_html = """
    <div style="padding: 1rem; background: #2d2d44; border-radius: 10px; margin: 1rem 0;">
        <button id="voiceBtn" onclick="startVoiceRecognition()" style="
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0 auto;
        ">
            🎤 Start Voice Recording
        </button>
        <p id="voiceStatus" style="text-align: center; margin-top: 0.5rem; color: #888;"></p>
        <textarea id="voiceResult" style="
            width: 100%;
            min-height: 80px;
            margin-top: 1rem;
            padding: 0.5rem;
            border-radius: 8px;
            border: 1px solid #3d3d5c;
            background: #1e1e2e;
            color: white;
            display: none;
        "></textarea>
    </div>
    
    <script>
        function startVoiceRecognition() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                document.getElementById('voiceStatus').innerText = 'Voice recognition not supported in this browser';
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            const btn = document.getElementById('voiceBtn');
            const status = document.getElementById('voiceStatus');
            const result = document.getElementById('voiceResult');
            
            btn.innerHTML = '🔴 Recording...';
            btn.style.background = '#dc3545';
            status.innerText = 'Listening... Speak now';
            
            recognition.onresult = function(event) {
                let transcript = '';
                for (let i = 0; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                result.value = transcript;
                result.style.display = 'block';
            };
            
            recognition.onend = function() {
                btn.innerHTML = '🎤 Start Voice Recording';
                btn.style.background = 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
                status.innerText = 'Recording complete. Copy the text below and paste it in the Text Input tab.';
            };
            
            recognition.onerror = function(event) {
                btn.innerHTML = '🎤 Start Voice Recording';
                btn.style.background = 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
                status.innerText = 'Error: ' + event.error;
            };
            
            recognition.start();
        }
    </script>
    """
    
    st.components.v1.html(voice_input_html, height=250)
    
    st.info("💡 After voice recording, copy the transcribed text and paste it in the **Text Input** tab to submit.")

st.divider()

# Chat display area
st.markdown("### 💬 Conversation")

# Display chat messages
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #888;">
            <h3>👋 Welcome to Code Gen AI!</h3>
            <p>Start a conversation by entering a prompt above.</p>
            <p>Choose between <strong>Code Generation</strong> or <strong>Code Explanation</strong> mode.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])

# Process new input
if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # Generate and display assistant response
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""
        
        with st.spinner(f"🔄 {'Generating code' if feature_mode == 'Code Generation' else 'Analyzing code'}..."):
            try:
                for chunk in generate_response(user_input, selected_model, feature_mode):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"❌ Error generating response: {str(e)}"
                response_placeholder.error(full_response)
    
    # Add assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
    
    # Save chat
    save_current_chat()
    
    st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 Code Gen AI - Powered by LLMs | Built with Streamlit</p>
    <p style="font-size: 0.8rem;">Models: GPT-OSS-120B (Groq) • LLaMA 3 • DeepSeek-R1</p>
</div>
""", unsafe_allow_html=True)
