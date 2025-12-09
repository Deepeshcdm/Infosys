# # """Streamlit ChatGPT-style frontend tailored for coding workflows."""

# # import re
# # from typing import Any, Dict, List

# # import streamlit as st


# # CHAT_MODES = ["Generate Code", "Explain Code"]
# # MODEL_OPTIONS = ["gpt-5-mini", "gpt-5-mini-code", "custom-model"]
# # DEFAULT_SYSTEM_PROMPT = "You are a senior AI pair programmer who writes and explains clean code."
# # CODE_BLOCK_PATTERN = re.compile(r"```(?P<lang>[\w+\-]*)\n(?P<code>.*?)```", re.DOTALL)



# # def create_persistent_chat(title: str = "New chat") -> str:
# #     """Create a saved conversation and return its identifier."""
# #     chat_id = str(st.session_state.chat_counter)
# #     st.session_state.chat_counter += 1
# #     st.session_state.chats[chat_id] = {"title": title, "messages": []}
# #     return chat_id


# # def ensure_current_chat() -> None:
# #     """Make sure we have at least one persistent chat selected."""
# #     if not st.session_state.chats:
# #         chat_id = create_persistent_chat()
# #         st.session_state.current_chat_id = chat_id
# #     elif st.session_state.current_chat_id not in st.session_state.chats:
# #         st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))


# # def init_session_state() -> None:
# #     """Bootstrap all keys required by the UI."""
# #     st.session_state.setdefault("chat_counter", 1)
# #     st.session_state.setdefault("chats", {})
# #     st.session_state.setdefault("current_chat_id", "")
# #     st.session_state.setdefault("is_temp_chat", False)
# #     st.session_state.setdefault("temp_messages", [])
# #     st.session_state.setdefault("display_name", "Developer")
# #     st.session_state.setdefault("mode_select", CHAT_MODES[0])
# #     st.session_state.setdefault("model_select", MODEL_OPTIONS[0])
# #     st.session_state.setdefault("system_prompt_area", DEFAULT_SYSTEM_PROMPT)
# #     st.session_state.setdefault("show_search_box", False)
# #     st.session_state.setdefault("chat_search", "")
# #     st.session_state.setdefault("sidebar_notice", "")

# #     ensure_current_chat()


# # def inject_custom_css() -> None:
# #     """Inject a lightweight dark theme + sidebar styling to mimic ChatGPT."""
# #     st.markdown(
# #         """
# #         <style>
# #         :root { color-scheme: dark; }
# #         body, .stApp, .block-container {
# #             background-color: #050509;
# #             color: #f5f7ff;
# #         }
# #         .block-container {
# #             padding-top: 2.5rem;
# #             padding-bottom: 5rem;
# #             max-width: 900px;
# #         }
# #         div[data-testid="stSidebar"] {
# #             background-color: #0c0f1a;
# #             border-right: 1px solid #191d2d;
# #         }
# #         div[data-testid="stSidebar"] * {
# #             color: #e0e6ff !important;
# #         }
# #         .sidebar-logo {
# #             font-size: 1.05rem;
# #             letter-spacing: 0.08em;
# #             text-transform: uppercase;
# #             font-weight: 600;
# #             display: flex;
# #             align-items: center;
# #             gap: 0.4rem;
# #             margin-bottom: 1rem;
# #         }
# #         .sidebar-nav {
# #             display: flex;
# #             flex-direction: column;
# #             gap: 0.35rem;
# #             margin: 1rem 0 1.4rem 0;
# #         }
# #         .sidebar-nav-item {
# #             display: flex;
# #             align-items: center;
# #             gap: 0.55rem;
# #             padding: 0.45rem 0.75rem;
# #             border-radius: 12px;
# #             border: 1px solid rgba(255,255,255,0.05);
# #             background: rgba(255,255,255,0.02);
# #             font-size: 0.9rem;
# #         }
# #         .sidebar-section-title {
# #             text-transform: uppercase;
# #             font-size: 0.75rem;
# #             letter-spacing: 0.14em;
# #             color: #8f96c2;
# #             margin-bottom: 0.4rem;
# #         }
# #         .shortcut-btn button,
# #         .shortcut-row button {
# #             width: 100%;
# #             border-radius: 12px;
# #             border: 1px solid rgba(255,255,255,0.05);
# #             background: rgba(255,255,255,0.02);
# #             font-size: 0.9rem;
# #             padding: 0.45rem 0.6rem;
# #         }
# #         .shortcut-row button {
# #             font-size: 0.85rem;
# #             padding: 0.35rem 0.45rem;
# #         }
# #         .gpt-pill-row {
# #             display: flex;
# #             gap: 0.5rem;
# #         }
# #         .gpt-pill {
# #             padding: 0.35rem 0.85rem;
# #             border-radius: 999px;
# #             border: 1px solid #2f3547;
# #             font-size: 0.85rem;
# #             color: #dfe4ff;
# #             background: rgba(255,255,255,0.04);
# #         }
# #         .chat-item-radio div[role="radiogroup"] > div {
# #             background: rgba(255,255,255,0.02);
# #             border: 1px solid rgba(255,255,255,0.05);
# #             padding: 0.4rem 0.6rem;
# #             border-radius: 12px;
# #             margin-bottom: 0.35rem;
# #         }
# #         .chat-item-radio label {
# #             width: 100%;
# #         }
# #         .chat-item-radio div[role="radiogroup"] input:checked + div {
# #             border-color: #7a83ff;
# #             background: rgba(122,131,255,0.08);
# #         }
# #         div[data-testid="stChatMessage"] {
# #             margin-bottom: 1.2rem;
# #         }
# #         .chat-bubble {
# #             width: 100%;
# #             border-radius: 18px;
# #             border: 1px solid #1f2335;
# #             padding: 1rem 1.25rem;
# #             margin-top: 0.25rem;
# #             box-shadow: 0 0 40px rgba(4, 6, 15, 0.65);
# #             background: #0e1425;
# #         }
# #         .assistant-bubble { background: linear-gradient(145deg, #10182d, #0b0f1a); }
# #         .user-bubble { background: linear-gradient(145deg, #1c2339, #13192b); }
# #         .hero-card {
# #             text-align: center;
# #             margin: 6rem auto 4rem auto;
# #             padding: 4rem 2rem;
# #             max-width: 680px;
# #         }
# #         .hero-pill {
# #             display: inline-flex;
# #             border: 1px solid #2f3244;
# #             border-radius: 999px;
# #             padding: 0.15rem 0.9rem;
# #             font-size: 0.9rem;
# #             letter-spacing: 0.08em;
# #             text-transform: uppercase;
# #             color: #9ea3c7;
# #             margin-bottom: 1rem;
# #         }
# #         .hero-title {
# #             font-size: clamp(2.5rem, 5vw, 3.6rem);
# #             font-weight: 600;
# #             color: #f9fbff;
# #             margin-bottom: 0.6rem;
# #         }
# #         .hero-subtitle { color: #99a1c7; font-size: 1.2rem; }
# #         div[data-testid="stChatInput"] > div {
# #             border: 1px solid #20283d;
# #             border-radius: 22px;
# #             background: #0d1322;
# #             padding: 0.4rem 0.6rem;
# #             box-shadow: 0 10px 45px rgba(5, 8, 20, 0.45);
# #         }
# #         div[data-testid="stChatInput"] textarea {
# #             background: transparent !important;
# #             color: #f5f7ff !important;
# #         }
# #         div[data-testid="stSidebar"] button {
# #             border-radius: 16px;
# #             border: 1px solid #2f3547;
# #             background: #161c2e;
# #         }
# #         div[data-testid="stSidebar"] button:hover {
# #             border-color: #6b72ff;
# #         }
# #         </style>
# #         """,
# #         unsafe_allow_html=True,
# #     )


# # def set_sidebar_notice(message: str) -> None:
# #     """Store a short notice message for sidebar alerts."""
# #     st.session_state.sidebar_notice = message


# # def get_active_messages() -> List[Dict[str, Any]]:
# #     """Return the list that represents the active conversation."""
# #     if st.session_state.is_temp_chat:
# #         return st.session_state.temp_messages
# #     return st.session_state.chats[st.session_state.current_chat_id]["messages"]


# # def parse_and_render_segments(content: str) -> None:
# #     """Render Markdown text mixed with fenced code blocks."""
# #     start = 0
# #     for match in CODE_BLOCK_PATTERN.finditer(content):
# #         text_chunk = content[start : match.start()].strip()
# #         if text_chunk:
# #             st.markdown(text_chunk)

# #         language = match.group("lang") or "text"
# #         st.code(match.group("code"), language=language.strip())
# #         start = match.end()

# #     tail = content[start:].strip()
# #     if tail:
# #         st.markdown(tail)


# # def render_chat_history(messages: List[Dict[str, Any]]) -> None:
# #     """Loop through session messages and display them with avatars and bubbles."""
# #     for message in messages:
# #         role = message.get("role", "assistant")
# #         avatar = "🧑" if role == "user" else "🤖"
# #         with st.chat_message(role, avatar=avatar):
# #             bubble_class = "user-bubble" if role == "user" else "assistant-bubble"
# #             st.markdown(f"<div class='chat-bubble {bubble_class}'>", unsafe_allow_html=True)
# #             parse_and_render_segments(message.get("content", ""))
# #             st.markdown("</div>", unsafe_allow_html=True)


# # def render_empty_state(display_name: str) -> None:
# #     """Hero section that mirrors ChatGPT's welcome card when chat is empty."""
# #     st.markdown(
# #         f"""
# #         <div class="hero-card">
# #             <div class="hero-pill">CODE GEN AI</div>
# #             <div class="hero-title">Hey, {display_name}. Ready to dive in?</div>
# #             <div class="hero-subtitle">Ask anything about code — generation, debugging, or explanation.</div>
# #         </div>
# #         """,
# #         unsafe_allow_html=True,
# #     )


# # def clear_conversation() -> None:
# #     """Clear only the currently active conversation."""
# #     messages = get_active_messages()
# #     messages.clear()


# # def summarize_title(prompt: str) -> str:
# #     """Generate a short title from the first user message."""
# #     condensed = prompt.strip().splitlines()[0][:36]
# #     return condensed + ("…" if len(prompt.strip()) > len(condensed) else "") or "New chat"


# # def send_to_backend(
# #     messages: List[Dict[str, Any]],
# #     *,
# #     mode: str,
# #     system_prompt: str,
# #     model: str,
# # ) -> str:
# #     """Stub that simulates an assistant reply."""
# #     user_prompt = next(
# #         (msg.get("content", "") for msg in reversed(messages) if msg.get("role") == "user"),
# #         "",
# #     )

# #     if not user_prompt:
# #         return "I'm ready whenever you are. Ask me something about code!"

# #     if mode == "Generate Code":
# #         return (
# #             "Here's a quick scaffold inspired by your request. Customize or expand it once you plug in "
# #             "your Ollama backend.\n\n"
# #             "```python\n"
# #             "def generated_solution(*args, **kwargs):\n"
# #             "    \"\"\"Auto-generated stub based on your latest prompt.\"\"\"\n"
# #             "    # TODO: replace with the logic you need\n"
# #             "    raise NotImplementedError('Hook this up to your Ollama call')\n"
# #             "```\n\n"
# #             "**What to do next**\n"
# #             "1. Replace this stub with code streamed from your model.\n"
# #             "2. Use the system prompt to enforce style or testing preferences.\n"
# #             f"3. Model selector currently reads `{model}` for you to map to a real deployment."
# #         )

# #     if mode == "Explain Code":
# #         summary = (
# #             "I scanned the snippet you shared and prepared a concise explanation. "
# #             "Swap this out with a real analysis response once Ollama is wired up."
# #         )
# #         bullets = (
# #             "- **What it does:** Parses your input, performs the described transformation, and returns the result.\n"
# #             "- **Key considerations:** Consider adding docstrings, logging, and unit tests.\n"
# #             "- **Complexity:** Roughly O(n) with respect to the input size.\n"
# #         )
# #         return f"{summary}\n\n{bullets}\n\nLet me know if you want a refactor or test suite."

# #     return (
# #         "Frontend is live! Pick a mode in the sidebar or wire `send_to_backend` to Ollama "
# #         "for real responses."
# #     )


# # def handle_user_prompt(user_prompt: str, mode: str, system_prompt: str, model: str) -> None:
# #     """Persist the new user prompt, get assistant reply, and re-render."""
# #     messages = get_active_messages()
# #     messages.append({"role": "user", "content": user_prompt})
# #     assistant_reply = send_to_backend(
# #         messages,
# #         mode=mode,
# #         system_prompt=system_prompt,
# #         model=model,
# #     )
# #     messages.append({"role": "assistant", "content": assistant_reply})

# #     if not st.session_state.is_temp_chat:
# #         chat_meta = st.session_state.chats[st.session_state.current_chat_id]
# #         if chat_meta["title"] == "New chat" and user_prompt.strip():
# #             chat_meta["title"] = summarize_title(user_prompt)


# # def start_new_chat() -> None:
# #     """Start a fresh conversation respecting the temp toggle."""
# #     if st.session_state.is_temp_chat:
# #         st.session_state.temp_messages = []
# #     else:
# #         chat_id = create_persistent_chat()
# #         st.session_state.current_chat_id = chat_id


# # def render_chat_list() -> None:
# #     """Renderable list of saved chats similar to ChatGPT sidebar."""
# #     if not st.session_state.chats:
# #         st.caption("No saved chats yet. Start typing to create one.")
# #         return

# #     chat_ids = list(st.session_state.chats.keys())
# #     query = st.session_state.chat_search.strip().lower()
# #     if query:
# #         chat_ids = [cid for cid in chat_ids if query in st.session_state.chats[cid]["title"].lower()]
# #         if not chat_ids:
# #             st.caption("No chats match your search.")
# #             return

# #     current_id = st.session_state.current_chat_id
# #     if current_id not in chat_ids:
# #         current_id = chat_ids[0]
# #         st.session_state.current_chat_id = current_id

# #     index = chat_ids.index(current_id)
# #     selection = st.radio(
# #         "Your chats",
# #         options=chat_ids,
# #         index=index,
# #         format_func=lambda cid: st.session_state.chats[cid]["title"],
# #         label_visibility="collapsed",
# #         key="chat_history_selector",
# #     )
# #     if selection != current_id:
# #         st.session_state.current_chat_id = selection


# # def render_sidebar() -> tuple[str, str, str]:
# #     """Full sidebar layout including nav, GPTs, chats, and assistant controls."""
# #     with st.sidebar:
# #         st.markdown('<div class="sidebar-logo">⚪ CODE GEN AI</div>', unsafe_allow_html=True)
# #         if st.button("＋ New chat", use_container_width=True):
# #             start_new_chat()

# #         st.markdown('<div class="sidebar-section-title">Shortcuts</div>', unsafe_allow_html=True)
# #         if st.button("🔍 Search chats", key="nav_search", use_container_width=True):
# #             st.session_state.show_search_box = not st.session_state.show_search_box
# #             if not st.session_state.show_search_box:
# #                 st.session_state.chat_search = ""

# #         if st.session_state.show_search_box:
# #             st.text_input(
# #                 "Search your conversations",
# #                 key="chat_search",
# #                 placeholder="Type to filter chat titles",
# #             )

# #         col1, col2 = st.columns(2)
# #         with col1:
# #             if st.button("📚 Library", key="nav_library", use_container_width=True):
# #                 set_sidebar_notice("Library is a placeholder — connect docs or snippets later.")
# #         with col2:
# #             if st.button("🗂️ Projects", key="nav_projects", use_container_width=True):
# #                 set_sidebar_notice("Projects hub coming soon. Map repos or tasks here.")

# #         if st.session_state.sidebar_notice:
# #             st.info(st.session_state.sidebar_notice)
# #             if st.button("Dismiss", key="nav_dismiss", use_container_width=True):
# #                 st.session_state.sidebar_notice = ""

# #         temp_toggle = st.toggle(
# #             "Temporary chat",
# #             value=st.session_state.is_temp_chat,
# #             help="When enabled, chats are not saved to history.",
# #         )
# #         if temp_toggle != st.session_state.is_temp_chat:
# #             st.session_state.is_temp_chat = temp_toggle
# #             if temp_toggle:
# #                 st.session_state.temp_messages = []
# #             else:
# #                 ensure_current_chat()

# #         if st.session_state.is_temp_chat:
# #             st.caption("Temporary chat is on. Nothing will show up under 'Your chats'.")
# #         else:
# #             st.markdown('<div class="sidebar-section-title">Your chats</div>', unsafe_allow_html=True)
# #             with st.container():
# #                 st.markdown('<div class="chat-item-radio">', unsafe_allow_html=True)
# #                 render_chat_list()
# #                 st.markdown('</div>', unsafe_allow_html=True)

          
# #         st.markdown("---")
# #         st.subheader("Assistant Controls")
# #         display_name = st.text_input("Display name", value=st.session_state.display_name)
# #         st.session_state.display_name = display_name or "Developer"

# #         mode = st.selectbox("Mode", options=CHAT_MODES, key="mode_select")
# #         model = st.selectbox("Model (placeholder)", options=MODEL_OPTIONS, key="model_select")
# #         system_prompt = st.text_area(
# #             "System prompt",
# #             value=DEFAULT_SYSTEM_PROMPT,
# #             height=120,
# #             key="system_prompt_area",
# #         )

# #         if st.button("Clear conversation", use_container_width=True):
# #             clear_conversation()
# #             st.rerun()

# #         st.caption("Backend stub: edit `send_to_backend` in FrontEnd.py to call Ollama/OpenAI.")

# #     return mode, model, system_prompt


# # def main() -> None:
# #     st.set_page_config(page_title="ChatGPT-style Code Companion", layout="wide")
# #     inject_custom_css()
# #     init_session_state()

# #     mode, model, system_prompt = render_sidebar()
# #     messages = get_active_messages()

# #     if messages:
# #         render_chat_history(messages)
# #     else:
# #         render_empty_state(st.session_state.display_name)

# #     user_prompt = st.chat_input("Ask anything about your code...")
# #     if user_prompt:
# #         handle_user_prompt(user_prompt.strip(), mode, system_prompt.strip(), model)
# #         st.rerun()


# # if __name__ == "__main__":
# #     main()

# # streamlit_app.py
# import json
# import time
# from typing import Optional

# import requests
# import streamlit as st

# # ---- Config ----
# try:
#     OLLAMA_BASE = st.secrets["OLLAMA_BASE"]
# except Exception:
#     OLLAMA_BASE = "http://127.0.0.1:11434"

# MODEL = "llama3"

# st.title("Streamlit + Ollama /api/chat")

# prompt = st.text_area("Prompt", value="why is the sky blue?", height=120)
# streaming = st.checkbox("Stream tokens (live)", value=True)

# col1, col2 = st.columns([1, 4])
# with col1:
#     btn = st.button("Generate")

# output_area = st.empty()


# def call_ollama_chat_non_stream(prompt: str, model: str) -> str:
#     """
#     Non-streaming call to /api/chat with stream=false.
#     Returns the final assistant message content.
#     """
#     payload = {
#         "model": model,
#         "stream": False,
#         "messages": [
#             {"role": "user", "content": prompt}
#         ],
#     }

#     r = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=300)
#     r.raise_for_status()

#     data = r.json()
#     # Expected shape (like the one you pasted):
#     # {
#     #   "model": "...",
#     #   "message": { "role": "assistant", "content": "..." },
#     #   ...
#     # }
#     message = data.get("message", {})
#     content = message.get("content", "")
#     if not content:
#         # Fallback: just show raw JSON if unexpected
#         return json.dumps(data, indent=2, ensure_ascii=False)
#     return content


# def call_ollama_chat_stream(prompt: str, model: str):
#     """
#     Streaming call to /api/chat with stream=true.
#     Yields the accumulated assistant content as it arrives.
#     Ollama streams NDJSON objects, one per line.
#     """
#     payload = {
#         "model": model,
#         "stream": True,
#         "messages": [
#             {"role": "user", "content": prompt}
#         ],
#     }

#     with requests.post(
#         f"{OLLAMA_BASE}/api/chat", json=payload, stream=True, timeout=0
#     ) as r:
#         r.raise_for_status()

#         buffer = ""
#         for line in r.iter_lines(decode_unicode=True):
#             if not line:
#                 continue

#             try:
#                 obj = json.loads(line)
#             except json.JSONDecodeError:
#                 # If for some reason it's not JSON, just append raw
#                 buffer += line
#                 yield buffer
#                 continue

#             # Typical streamed chunk looks like:
#             # {
#             #   "model": "...",
#             #   "message": {"role": "assistant", "content": "piece"},
#             #   "done": false | true,
#             #   ...
#             # }
#             msg = obj.get("message") or {}
#             piece = msg.get("content", "")

#             if piece:
#                 buffer += piece
#                 yield buffer

#             if obj.get("done"):
#                 break


# if btn:
#     output_area.markdown("**Generating...**")
#     try:
#         if streaming:
#             partial = output_area.empty()
#             for buf in call_ollama_chat_stream(prompt, MODEL):
#                 partial.code(buf)
#             output_area.success("Done.")
#         else:
#             resp = call_ollama_chat_non_stream(prompt, MODEL)
#             output_area.code(resp)
#     except requests.HTTPError as e:
#         output_area.error(
#             f"Request failed: {e} — {getattr(e.response, 'text', '')}"
#         )
#     except Exception as e:
#         output_area.error(f"Unexpected error: {e}")
from google import genai
import os


