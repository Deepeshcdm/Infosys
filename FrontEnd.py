# """Streamlit ChatGPT-style frontend with image and voice input support."""
# """
# The Python script is a Streamlit frontend for a ChatGPT-style chat interface with support for image
# and voice input, allowing users to interact with an AI assistant for various tasks.

# :param title: The `title` parameter in the code is used to specify the title of a chat conversation.
# It can be provided when creating a new chat or when updating the title of an existing chat. The
# title helps identify and differentiate between different chat conversations, making it easier for
# users to manage and navigate through their
# :type title: Optional[str]
# :return: The code provided is a Streamlit frontend application that simulates a chat interface with
# ChatGPT-style functionality. It includes features such as image and voice input support. The code
# defines functions for creating and managing chat conversations, rendering chat history, handling
# user prompts, injecting custom CSS for styling, and interacting with the backend to generate
# responses based on user input.
# """

import base64
import io
import json
import re
from typing import Any, Dict, List, Optional

import streamlit as st
from PIL import Image
import os
import requests
from streamlit.errors import StreamlitSecretNotFoundError

# If you prefer to hardcode an API key directly in this file (not recommended for production),
# put it here as a string. Leave empty to use environment or Streamlit secrets.
#"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" = ""
GROQ_BASE_URL_DIRECT = ""
GEMINI_API_KEY_DIRECT = ""
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Audio processing imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


CHAT_MODES = ["Chat", "Generate Code", "Explain Code"]
MODEL_OPTIONS = ["gpt-oss-120b", "llama3", "deepseek-r1", "qwen3-vl:2b"]
DEFAULT_SYSTEM_PROMPT = "You are ChatGPT, a large language model trained by OpenAI. You are helpful, creative, clever, and very friendly."
CODE_BLOCK_PATTERN = re.compile(r"```(?P<lang>[\w+\-]*)\n(?P<code>.*?)```", re.DOTALL)


def get_secret_or_env(key: str) -> Optional[str]:
    """Fetch a secret from environment first, then Streamlit secrets (safely)."""
    env_val = os.environ.get(key)
    if env_val:
        return env_val
    try:
        if hasattr(st, "secrets"):
            return st.secrets.get(key)
    except StreamlitSecretNotFoundError:
        return None
    except Exception:
        return None
    return None


def create_persistent_chat(title: Optional[str] = None) -> str:
    """Create a saved conversation and return its identifier."""
    chat_id = str(st.session_state.chat_counter)
    st.session_state.chat_counter += 1
    default_title = title or f"New chat {chat_id}"
    st.session_state.chats[chat_id] = {"title": default_title, "messages": []}
    return chat_id


def ensure_current_chat() -> None:
    """Make sure we have at least one persistent chat selected."""
    if not st.session_state.chats:
        chat_id = create_persistent_chat()
        st.session_state.current_chat_id = chat_id
    elif st.session_state.current_chat_id not in st.session_state.chats:
        st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))


def init_session_state() -> None:
    """Bootstrap all keys required by the UI."""
    st.session_state.setdefault("chat_counter", 1)
    st.session_state.setdefault("chats", {})
    st.session_state.setdefault("current_chat_id", "")
    st.session_state.setdefault("is_temp_chat", False)
    st.session_state.setdefault("temp_messages", [])
    st.session_state.setdefault("display_name", "User")
    st.session_state.setdefault("mode_select", CHAT_MODES[0])
    st.session_state.setdefault("model_select", MODEL_OPTIONS[0])
    st.session_state.setdefault("system_prompt_area", DEFAULT_SYSTEM_PROMPT)
    st.session_state.setdefault("show_search_box", False)
    st.session_state.setdefault("chat_search", "")
    st.session_state.setdefault("sidebar_notice", "")
    st.session_state.setdefault("uploaded_image", None)
    st.session_state.setdefault("voice_text", "")
    st.session_state.setdefault("show_image_upload", False)
    st.session_state.setdefault("show_voice_input", False)
    st.session_state.setdefault("new_chat_name", "")
    st.session_state.setdefault("show_rename_input", False)
    st.session_state.setdefault("rename_chat_title", "")
    st.session_state.setdefault("auto_send_voice", False)

    ensure_current_chat()


def inject_custom_css() -> None:
    """Inject Code Gen AI-inspired dark theme styling."""
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        body, .stApp, .block-container {
            background-color: #212121;
            color: #ececec;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 6rem;
            max-width: 800px;
        }
        div[data-testid="stSidebar"] {
            background-color: #171717;
            border-right: 1px solid #2f2f2f;
        }
        div[data-testid="stSidebar"] * {
            color: #ececec !important;
        }
        .sidebar-logo {
            font-size: 1.1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            padding: 0.5rem;
        }
        .sidebar-section-title {
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            color: #8e8e8e;
            margin: 1.5rem 0 0.5rem 0;
            font-weight: 500;
        }
        div[data-testid="stChatMessage"] {
            margin-bottom: 0;
            padding: 1.5rem 0;
        }
        .chat-bubble {
            width: 100%;
            line-height: 1.6;
        }
        .assistant-bubble { 
            background: transparent;
        }
        .user-bubble { 
            background: transparent;
        }
        .hero-card {
            text-align: center;
            margin: 4rem auto 2rem auto;
            padding: 2.5rem;
            max-width: 700px;
            position: relative;
        }
        .hero-glow {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(16, 163, 127, 0.15) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            animation: glow-pulse 4s ease-in-out infinite;
        }
        @keyframes glow-pulse {
            0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
        }
        .hero-logo {
            width: 80px;
            height: 80px;
            border-radius: 24px;
            background: linear-gradient(135deg, #10a37f 0%, #0d8c6d 50%, #076d54 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem auto;
            font-size: 2.2rem;
            box-shadow: 0 20px 40px rgba(16, 163, 127, 0.3), 0 0 60px rgba(16, 163, 127, 0.1);
            animation: float 3s ease-in-out infinite;
            position: relative;
            z-index: 1;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.75rem;
            letter-spacing: -0.02em;
        }
        .hero-subtitle { 
            color: #8e8e8e; 
            font-size: 1.1rem;
            margin-bottom: 2.5rem;
            line-height: 1.6;
        }
        .hero-badges {
            display: flex;
            justify-content: center;
            gap: 0.75rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        .hero-badge {
            background: rgba(16, 163, 127, 0.1);
            border: 1px solid rgba(16, 163, 127, 0.3);
            border-radius: 20px;
            padding: 0.4rem 0.9rem;
            font-size: 0.75rem;
            color: #10a37f;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .suggestion-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            max-width: 600px;
            margin: 0 auto;
        }
        .suggestion-card {
            background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%);
            border: 1px solid #3a3a3a;
            border-radius: 16px;
            padding: 1.25rem;
            text-align: left;
            font-size: 0.9rem;
            color: #ececec;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .suggestion-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(16, 163, 127, 0.1) 0%, transparent 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .suggestion-card:hover {
            border-color: #10a37f;
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(16, 163, 127, 0.2);
        }
        .suggestion-card:hover::before {
            opacity: 1;
        }
        .suggestion-icon {
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
            display: block;
        }
        .suggestion-title {
            font-weight: 600;
            margin-bottom: 0.3rem;
            color: #fff;
        }
        .suggestion-desc {
            font-size: 0.8rem;
            color: #8e8e8e;
            line-height: 1.4;
        }
        div[data-testid="stChatInput"] > div {
            border: 1px solid #424242;
            border-radius: 24px;
            background: #2f2f2f;
            padding: 0.25rem 0.5rem;
        }
        div[data-testid="stChatInput"] textarea {
            background: transparent !important;
            color: #ececec !important;
        }
        div[data-testid="stSidebar"] button {
            border-radius: 8px;
            border: 1px solid #424242;
            background: #2f2f2f;
            transition: all 0.2s;
        }
        div[data-testid="stSidebar"] button:hover {
            background: #424242;
        }
        .input-toolbar {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            padding: 0 0.5rem;
        }
        .toolbar-btn {
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            color: #ececec;
            cursor: pointer;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .toolbar-btn:hover {
            background: #424242;
        }
        .toolbar-btn.active {
            background: #10a37f;
            border-color: #10a37f;
        }
        .image-preview {
            max-width: 300px;
            border-radius: 12px;
            margin: 0.5rem 0;
            border: 1px solid #424242;
        }
        .voice-status {
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .voice-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10a37f;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.1); }
        }
        .model-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 6px;
            padding: 0.25rem 0.6rem;
            font-size: 0.75rem;
            color: #8e8e8e;
        }
        .attachment-preview {
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 12px;
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .attachment-preview img {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 8px;
        }
        .attachment-info {
            flex: 1;
        }
        .attachment-name {
            font-size: 0.85rem;
            color: #ececec;
        }
        .attachment-size {
            font-size: 0.75rem;
            color: #8e8e8e;
        }
        .remove-attachment {
            color: #8e8e8e;
            cursor: pointer;
            font-size: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_sidebar_notice(message: str) -> None:
    """Store a short notice message for sidebar alerts."""
    st.session_state.sidebar_notice = message


def get_active_messages() -> List[Dict[str, Any]]:
    """Return the list that represents the active conversation."""
    if st.session_state.is_temp_chat:
        return st.session_state.temp_messages
    return st.session_state.chats[st.session_state.current_chat_id]["messages"]


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio to text using speech recognition."""
    if not SPEECH_RECOGNITION_AVAILABLE:
        return "[Speech recognition not available. Install: pip install SpeechRecognition]"
    
    recognizer = sr.Recognizer()
    
    try:
        # Convert audio bytes to AudioFile
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        
        # Use Google's free speech recognition
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "[Could not understand audio]"
    except sr.RequestError as e:
        return f"[Speech recognition error: {e}]"
    except Exception as e:
        return f"[Audio processing error: {e}]"


def stream_generate(model: str, prompt: str, image: Optional[Image.Image] = None):
    """Stream generate response from Ollama API as a generator."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    if image is not None:
        encoded_image = image_to_base64(image)
        payload["image"] = {
            "name": "uploaded.png",
            "mime_type": "image/png",
            "data": encoded_image,
        }

    try:
        with requests.post(OLLAMA_API_URL, headers=headers, json=payload, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                
                line = raw_line.strip()
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
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
        yield f"[Error connecting to Ollama: {e}. Make sure Ollama is running locally.]"
    except Exception as e:
        yield f"[Ollama API error: {e}]"


def parse_and_render_segments(content: str) -> None:
    """Render Markdown text mixed with fenced code blocks."""
    start = 0
    for match in CODE_BLOCK_PATTERN.finditer(content):
        text_chunk = content[start : match.start()].strip()
        if text_chunk:
            st.markdown(text_chunk)

        language = match.group("lang") or "text"
        st.code(match.group("code"), language=language.strip())
        start = match.end()

    tail = content[start:].strip()
    if tail:
        st.markdown(tail)


def render_chat_history(messages: List[Dict[str, Any]]) -> None:
    """Loop through session messages and display them with avatars and bubbles."""
    for message in messages:
        role = message.get("role", "assistant")
        avatar = "👤" if role == "user" else "✨"
        
        with st.chat_message(role, avatar=avatar):
            # Show image if present in message
            if "image" in message and message["image"]:
                st.image(message["image"], width=300)
            
            st.markdown(f"<div class='chat-bubble'>", unsafe_allow_html=True)
            parse_and_render_segments(message.get("content", ""))
            st.markdown("</div>", unsafe_allow_html=True)


def set_empty_state_action(prefill_text: str, *, show_image_upload: bool = False) -> None:
    """Apply suggestion card action and optionally open the image uploader."""
    st.session_state.prefill_prompt = prefill_text
    if show_image_upload:
        st.session_state.show_image_upload = True
        st.session_state.show_voice_input = False


def render_empty_state(display_name: str) -> None:
    """Stunning ChatGPT-style welcome screen with animated suggestions."""
    
    # Get current model for display
    current_model = st.session_state.get("model_select", MODEL_OPTIONS[0])
    current_mode = st.session_state.get("mode_select", CHAT_MODES[0])
    
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-glow"></div>
            <div class="hero-logo">✨</div>
            <div class="hero-title">Hi {display_name}, how can I help?</div>
            <div class="hero-subtitle">
                I'm your AI coding assistant. Ask me anything, upload an image for analysis,<br>
                or use voice input to get started.
            </div>
            <div class="hero-badges">
                <span class="hero-badge">🤖 {current_model}</span>
                <span class="hero-badge">💬 {current_mode}</span>
                <span class="hero-badge">⚡ Streaming</span>
                <span class="hero-badge">🖼️ Vision</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Stunning suggestion cards
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Card 1: Explain
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">💡</span>
                <div class="suggestion-title">Explain a concept</div>
                <div class="suggestion-desc">Break down complex topics into simple terms</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "💡 Explain a concept",
            use_container_width=True,
            key="sug1",
            on_click=set_empty_state_action,
            args=("Explain how neural networks work in simple terms",),
        )
        
        # Card 3: Debug
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">🔧</span>
                <div class="suggestion-title">Debug my code</div>
                <div class="suggestion-desc">Find and fix bugs in your code</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "🔧 Debug my code",
            use_container_width=True,
            key="sug3",
            on_click=set_empty_state_action,
            args=("Help me debug this code: ",),
        )
            
    with col2:
        # Card 2: Write
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">✍️</span>
                <div class="suggestion-title">Write something</div>
                <div class="suggestion-desc">Generate emails, docs, or creative content</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "✍️ Write something",
            use_container_width=True,
            key="sug2",
            on_click=set_empty_state_action,
            args=("Write a professional email about ",),
        )
        
        # Card 4: Image
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">🖼️</span>
                <div class="suggestion-title">Analyze an image</div>
                <div class="suggestion-desc">Upload and get insights from images</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "🖼️ Analyze an image",
            use_container_width=True,
            key="sug4",
            on_click=set_empty_state_action,
            args=("",),
            kwargs={"show_image_upload": True},
        )
    


def clear_conversation() -> None:
    """Clear only the currently active conversation."""
    messages = get_active_messages()
    messages.clear()
    st.session_state.uploaded_image = None


def delete_chat(chat_id: str) -> None:
    """Remove a saved chat and keep selection valid."""
    if chat_id in st.session_state.chats:
        st.session_state.chats.pop(chat_id)
        if st.session_state.current_chat_id == chat_id:
            next_chat = next(iter(st.session_state.chats), "")
            if next_chat:
                st.session_state.current_chat_id = next_chat
            else:
                st.session_state.current_chat_id = create_persistent_chat()


def rename_chat(chat_id: str, new_title: str) -> None:
    """Rename a chat with a new title."""
    if chat_id in st.session_state.chats and new_title.strip():
        st.session_state.chats[chat_id]["title"] = new_title.strip()
        st.session_state.show_rename_input = False
        st.session_state.rename_chat_title = ""


def summarize_title(prompt: str) -> str:
    """Generate a short title from the first user message."""
    condensed = prompt.strip().splitlines()[0][:40]
    return condensed + ("…" if len(prompt.strip()) > len(condensed) else "") or "New chat"


def send_to_backend(
    messages: List[Dict[str, Any]],
    *,
    mode: str,
    system_prompt: str,
    model: str,
    image: Optional[Image.Image] = None,
):
    """Send messages to the selected backend model and yield assistant text chunks for streaming.

    Behavior:
    - If `model` == "gpt-oss-120b" use the Groq/OpenAI-compatible Responses API.
      The function will first attempt to use the `openai.OpenAI` SDK if available,
      otherwise it will POST to the configured `GROQ_BASE_URL` using `requests`.
    - For llama3/deepseek-r1, uses Ollama API.
    - For other modes/models the function falls back to a friendly stub message.

    Keys:
    - Put credentials in `st.secrets` or environment variables:
      - `GROQ_API_KEY` and optional `GROQ_BASE_URL` for Groq/OpenAI-compatible API
    """

    user_prompt = next(
        (msg.get("content", "") for msg in reversed(messages) if msg.get("role") == "user"),
        "",
    )

    # If there is an image, attach a short descriptor to the prompt
    if image is not None:
        try:
            b64 = image_to_base64(image)
            user_prompt = f"[Image attached: base64_png({len(b64)} bytes)]\n\n" + user_prompt
        except Exception:
            user_prompt = "[Image attached]\n\n" + user_prompt

    if not user_prompt:
        yield "Hi there! Send a message or upload an image and I'll respond."
        return
    
    # Apply mode-specific instructions to the prompt
    mode_instructions = ""
    if mode == "Generate Code":
        mode_instructions = "You are a code generation assistant. Generate clean, efficient, and well-commented code based on the user's request. Always include code examples in your response.\n\n"
    elif mode == "Explain Code":
        mode_instructions = "You are a code explanation assistant. Provide clear, detailed explanations of code, breaking down how it works step by step. Explain concepts, logic flow, and best practices.\n\n"
    else:  # Chat mode
        mode_instructions = f"{system_prompt}\n\n"
    
    # Prepend mode instructions to user prompt
    full_prompt = mode_instructions + user_prompt

    # --------------------
    # Groq / OpenAI-compatible (gpt-oss-120b)
    # --------------------
    if model == "gpt-oss-120b":
        groq_api_key = get_secret_or_env("GROQ_API_KEY")
        # allow hardcoded fallback for convenience during local testing
        if not groq_api_key and "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":
            groq_api_key = "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".strip() or None

        groq_base = get_secret_or_env("GROQ_BASE_URL") or GROQ_BASE_URL_DIRECT or "https://api.groq.com/openai/v1"
        if not groq_api_key:
            yield "[GROQ API key not found. Set `GROQ_API_KEY` in Streamlit secrets, environment variables, or `GROQ_API_KEY_DIRECT` in this file.]"
            return

        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=groq_api_key,
                base_url=groq_base,
            )
            
            response = client.responses.create(
                input=full_prompt,
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
        except ImportError:
            yield "[OpenAI SDK not installed. Install: pip install openai]"
        except Exception as http_err:
            yield f"[Error calling Groq/OpenAI endpoint: {http_err}]"
        return

    # --------------------
    # Ollama Models (llama3, deepseek-r1)
    # --------------------
    if model in ["llama3", "deepseek-r1", "qwen3-vl:2b"]:
        yield from stream_generate(model, full_prompt, image)
        return

    # --------------------
    # Mode-based helper behavior (existing helpful stubs)
    # --------------------
    if mode == "Generate Code":
        yield (
            f"Here's the code you requested! 🚀\n\n"
            "```python\n"
            "def solution(data):\n"
            '    """Generated based on your requirements."""\n'
            "    # Implementation goes here\n"
            "    result = process(data)\n"
            "    return result\n"
            "```\n\n"
            "**Key points:**\n"
            "- Clean and readable structure\n"
            "- Follows best practices\n"
            "- Ready to customize\n\n"
            "Would you like me to explain any part or make modifications?"
        )
        return

    if mode == "Explain Code":
        yield (
            "Let me break this down for you! 📚\n\n"
            "**Overview:**\n"
            "The code you shared performs a specific operation with clear logic.\n\n"
            "**Step-by-step explanation:**\n"
            "1. **Input handling** - Validates and processes input data\n"
            "2. **Core logic** - Performs the main computation\n"
            "3. **Output** - Returns the processed result\n\n"
            "**Complexity:** O(n) time, O(1) space\n\n"
            "Any questions about specific parts?"
        )
        return

    # Default fallback
    yield (
        f"Great question! Here's a friendly stub reply while the model call is not configured.\n\n"
        f"Your input: \"{user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}\"\n\n"
        f"Selected model: `{model}`\n"
        "To enable live responses, set API keys in Streamlit `secrets.toml` or environment variables and install the SDKs."
    )


def handle_user_prompt(
    user_prompt: str, 
    mode: str, 
    system_prompt: str, 
    model: str,
    image: Optional[Image.Image] = None
) -> None:
    """Persist the new user prompt, get assistant reply with streaming, and re-render."""
    messages = get_active_messages()
    
    # Create message with optional image
    user_message = {"role": "user", "content": user_prompt}
    if image:
        user_message["image"] = image
    
    messages.append(user_message)
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        if image:
            st.image(image, width=300)
        st.markdown(user_prompt)
    
    # Display streaming assistant response
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        full_response = ""
        
        for chunk in send_to_backend(
            messages,
            mode=mode,
            system_prompt=system_prompt,
            model=model,
            image=image,
        ):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    messages.append({"role": "assistant", "content": full_response})

    # Clear the uploaded image after sending
    st.session_state.uploaded_image = None

    if not st.session_state.is_temp_chat and user_prompt.strip():
        chat_meta = st.session_state.chats[st.session_state.current_chat_id]
        if chat_meta.get("title") in {"New chat", ""} or chat_meta.get("title", "").startswith("New chat "):
            chat_meta["title"] = summarize_title(user_prompt)


def start_new_chat(title: Optional[str] = None) -> None:
    """Start a fresh conversation respecting the temp toggle."""
    st.session_state.uploaded_image = None
    if st.session_state.is_temp_chat:
        st.session_state.temp_messages = []
    else:
        chat_id = create_persistent_chat(title)
        st.session_state.current_chat_id = chat_id


def handle_new_chat_button() -> None:
    """Callback for sidebar button to create a chat with custom title."""
    custom_title = st.session_state.get("new_chat_name", "").strip() or None
    start_new_chat(custom_title)
    st.session_state.new_chat_name = ""


def search_in_chat(chat_id: str, query: str) -> tuple[bool, str]:
    """Search for query in chat title and messages. Returns (found, match_type)."""
    chat = st.session_state.chats[chat_id]
    query_lower = query.lower()
    
    # Search in title
    if query_lower in chat["title"].lower():
        return True, "title"
    
    # Search in message content
    for message in chat.get("messages", []):
        content = message.get("content", "").lower()
        if query_lower in content:
            return True, "content"
    
    return False, ""


def render_chat_list() -> None:
    """Renderable list of saved chats similar to ChatGPT sidebar with enhanced search."""
    if not st.session_state.chats:
        st.caption("No saved chats yet.")
        return

    all_chat_ids = list(st.session_state.chats.keys())
    query = st.session_state.chat_search.strip().lower()
    
    # Enhanced search: filter by title or content
    if query:
        matched_chats = {}
        for cid in all_chat_ids:
            found, match_type = search_in_chat(cid, query)
            if found:
                matched_chats[cid] = match_type
        
        chat_ids = list(matched_chats.keys())
        
        if not chat_ids:
            st.warning(f"🔍 No chats found matching '{st.session_state.chat_search}'")
            st.caption("Try searching with different keywords or check your chat titles and messages.")
            return
        
        # Show search results count
        st.success(f"✓ Found {len(chat_ids)} chat(s) matching '{st.session_state.chat_search}'")
    else:
        chat_ids = all_chat_ids

    current_id = st.session_state.current_chat_id
    
    # Only switch to first result if current chat is not in the filtered list AND we have results
    if current_id not in chat_ids and chat_ids:
        # Don't auto-switch, just show the list without selection
        # User can click to switch
        index = 0
    else:
        index = chat_ids.index(current_id) if current_id in chat_ids else 0
    
    # Format function to show match indicator
    def format_chat_title(cid: str) -> str:
        title = st.session_state.chats[cid]["title"]
        if query:
            _, match_type = search_in_chat(cid, query)
            if match_type == "title":
                return f"📌 {title}"
            elif match_type == "content":
                return f"💬 {title}"
        return title
    
    selection = st.radio(
        "Your chats",
        options=chat_ids,
        index=index,
        format_func=format_chat_title,
        label_visibility="collapsed",
        key="chat_history_selector",
        help="📌 = Match in title, 💬 = Match in messages" if query else None
    )
    if selection != current_id:
        st.session_state.current_chat_id = selection
        st.rerun()

    # Chat actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Rename", key="rename_chat_btn", use_container_width=True):
            st.session_state.show_rename_input = not st.session_state.show_rename_input
            if st.session_state.show_rename_input:
                current_title = st.session_state.chats[st.session_state.current_chat_id]["title"]
                st.session_state.rename_chat_title = current_title
    
    with col2:
        if st.button("🗑️ Delete", key="delete_selected_chat", use_container_width=True):
            delete_chat(st.session_state.current_chat_id)
            st.rerun()
    
    # Rename input section
    if st.session_state.show_rename_input:
        new_title = st.text_input(
            "New chat title",
            value=st.session_state.rename_chat_title,
            key="rename_input",
            placeholder="Enter new title..."
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✓ Save", key="save_rename", use_container_width=True):
                if new_title.strip():
                    rename_chat(st.session_state.current_chat_id, new_title)
                    st.rerun()
        with col_b:
            if st.button("✕ Cancel", key="cancel_rename", use_container_width=True):
                st.session_state.show_rename_input = False
                st.rerun()


def render_sidebar() -> tuple[str, str, str]:
    """Full sidebar layout mimicking ChatGPT."""
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">✨ Code Gen AI</div>', unsafe_allow_html=True)
        
        st.text_input(
            "New chat name",
            key="new_chat_name",
            placeholder="Optional title",
        )
        st.button(
            "➕ New chat",
            use_container_width=True,
            on_click=handle_new_chat_button,
        )

        # Search
        st.markdown('<div class="sidebar-section-title">Search</div>', unsafe_allow_html=True)
        search = st.text_input(
            "Search chats",
            key="chat_search",
            placeholder="Search your chats...",
            label_visibility="collapsed"
        )

        # Temp chat toggle
        temp_toggle = st.toggle(
            "Temporary chat",
            value=st.session_state.is_temp_chat,
            help="Temporary chats won't be saved",
        )
        if temp_toggle != st.session_state.is_temp_chat:
            st.session_state.is_temp_chat = temp_toggle
            if temp_toggle:
                st.session_state.temp_messages = []
            else:
                ensure_current_chat()

        # Chat history
        if not st.session_state.is_temp_chat:
            st.markdown('<div class="sidebar-section-title">Recent</div>', unsafe_allow_html=True)
            render_chat_list()

        st.markdown("---")
        
        # Model & Settings
        st.markdown('<div class="sidebar-section-title">Settings</div>', unsafe_allow_html=True)
        
        model = st.selectbox(
            "Model",
            options=MODEL_OPTIONS,
            key="model_select",
            help="Select the AI model to use"
        )
        
        mode = st.selectbox(
            "Mode", 
            options=CHAT_MODES, 
            key="mode_select",
            help="Select conversation mode"
        )
        
        with st.expander("⚙️ Advanced"):
            display_name = st.text_input("Your name", value=st.session_state.display_name)
            st.session_state.display_name = display_name or "User"
            
            system_prompt = st.text_area(
                "System prompt",
                value=DEFAULT_SYSTEM_PROMPT,
                height=100,
                key="system_prompt_area",
            )

        if st.button("🗑️ Clear chat", use_container_width=True):
            clear_conversation()
            st.rerun()

    

    return mode, model, system_prompt


def render_input_toolbar() -> tuple[Optional[Image.Image], str]:
    """Render attachment toolbar with image and voice inputs."""
    uploaded_image = None
    voice_text = ""
    
    # Toolbar buttons
    col1, col2, col3 = st.columns([1, 1, 6])
    
    with col1:
        if st.button("📷 Image", key="img_btn", help="Upload an image"):
            st.session_state.show_image_upload = not st.session_state.show_image_upload
            st.session_state.show_voice_input = False
    
    with col2:
        if st.button("🎤 Voice", key="voice_btn", help="Voice input"):
            st.session_state.show_voice_input = not st.session_state.show_voice_input
            st.session_state.show_image_upload = False
    
    # Image upload section
    if st.session_state.show_image_upload:
        with st.container():
            uploaded_file = st.file_uploader(
                "Upload an image",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key="image_uploader",
                label_visibility="collapsed"
            )
            if uploaded_file:
                uploaded_image = Image.open(uploaded_file)
                st.session_state.uploaded_image = uploaded_image
                st.image(uploaded_image, width=200, caption="Ready to send")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ Keep", use_container_width=True):
                        st.session_state.show_image_upload = False
                with col_b:
                    if st.button("✕ Remove", use_container_width=True):
                        st.session_state.uploaded_image = None
                        st.rerun()
    
    # Voice input section
    if st.session_state.show_voice_input:
        with st.container():
            st.info("🎤 Record your voice message (auto-transcription enabled)")
            
            audio_value = st.audio_input(
                "Record your message",
                key="audio_recorder",
                label_visibility="collapsed"
            )
            
            if audio_value:
                st.audio(audio_value)
                
                # Auto-transcribe when audio is recorded
                if audio_value and "last_audio_hash" not in st.session_state or st.session_state.get("last_audio_hash") != hash(audio_value.getvalue()):
                    st.session_state.last_audio_hash = hash(audio_value.getvalue())
                    
                    with st.spinner("🎙️ Auto-transcribing..."):
                        audio_bytes = audio_value.read()
                        
                        if SPEECH_RECOGNITION_AVAILABLE:
                            tmp_path = None
                            try:
                                import wave
                                import tempfile
                                import os
                                import time
                                
                                # Save to temp file for speech recognition
                                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                    tmp.write(audio_bytes)
                                    tmp_path = tmp.name
                                
                                # Ensure file is closed before using it
                                time.sleep(0.1)
                                
                                recognizer = sr.Recognizer()
                                with sr.AudioFile(tmp_path) as source:
                                    audio_data = recognizer.record(source)
                                
                                # Ensure AudioFile is closed before cleanup
                                voice_text = recognizer.recognize_google(audio_data)
                                st.session_state.voice_text = voice_text
                                st.session_state.auto_send_voice = True
                                
                                st.success(f"✅ Transcribed: {voice_text}")
                                st.info("💬 Sending to AI automatically...")
                                st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Transcription error: {e}")
                                st.session_state.voice_text = ""
                            finally:
                                # Clean up temp file with retry
                                if tmp_path and os.path.exists(tmp_path):
                                    for i in range(3):  # Try 3 times
                                        try:
                                            os.unlink(tmp_path)
                                            break
                                        except PermissionError:
                                            time.sleep(0.1)  # Wait a bit and retry
                                        except Exception:
                                            break  # Give up on other errors
                        else:
                            st.warning("⚠️ Install `SpeechRecognition` for auto-transcription: `pip install SpeechRecognition`")
                
                # Manual transcribe button as backup
                col_manual, col_clear = st.columns(2)
                with col_manual:
                    if st.button("🔄 Re-transcribe", use_container_width=True):
                        with st.spinner("🎙️ Transcribing..."):
                            audio_bytes = audio_value.read()
                            
                            if SPEECH_RECOGNITION_AVAILABLE:
                                tmp_path = None
                                try:
                                    import wave
                                    import tempfile
                                    import os
                                    import time
                                    
                                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                        tmp.write(audio_bytes)
                                        tmp_path = tmp.name
                                    
                                    # Ensure file is closed before using it
                                    time.sleep(0.1)
                                    
                                    recognizer = sr.Recognizer()
                                    with sr.AudioFile(tmp_path) as source:
                                        audio_data = recognizer.record(source)
                                    
                                    # Ensure AudioFile is closed before cleanup
                                    voice_text = recognizer.recognize_google(audio_data)
                                    st.session_state.voice_text = voice_text
                                    
                                    st.success(f"✅ Re-transcribed: {voice_text}")
                                except Exception as e:
                                    st.error(f"❌ Transcription error: {e}")
                                finally:
                                    # Clean up temp file with retry
                                    if tmp_path and os.path.exists(tmp_path):
                                        for i in range(3):  # Try 3 times
                                            try:
                                                os.unlink(tmp_path)
                                                break
                                            except PermissionError:
                                                time.sleep(0.1)  # Wait a bit and retry
                                            except Exception:
                                                break  # Give up on other errors
                
                with col_clear:
                    if st.button("🗑️ Clear", use_container_width=True):
                        st.session_state.voice_text = ""
                        if "last_audio_hash" in st.session_state:
                            del st.session_state.last_audio_hash
                        st.rerun()
    
    # Show pending image preview
    if st.session_state.uploaded_image and not st.session_state.show_image_upload:
        with st.container():
            col_img, col_remove = st.columns([4, 1])
            with col_img:
                st.image(st.session_state.uploaded_image, width=80)
            with col_remove:
                if st.button("✕", key="remove_preview"):
                    st.session_state.uploaded_image = None
                    st.rerun()
    
    return st.session_state.uploaded_image, st.session_state.get("voice_text", "")


def main() -> None:
    st.set_page_config(
        page_title="Code Gen AI",
        page_icon="✨",
        layout="wide"
    )
    inject_custom_css()
    init_session_state()

    mode, model, system_prompt = render_sidebar()
    messages = get_active_messages()

    # Main chat area
    if messages:
        render_chat_history(messages)
    else:
        render_empty_state(st.session_state.display_name)

    # Input toolbar and chat input in linear layout
    st.markdown("---")
    
    # Create linear input layout: text input (left) -> voice (middle) -> image (right)
    input_col1, input_col2, input_col3 = st.columns([8, 0.8, 0.8])
    
    with input_col1:
        # Pre-fill prompt if set
        default_prompt = st.session_state.get("prefill_prompt", "")
        if default_prompt:
            st.session_state.prefill_prompt = ""
        
        # Use voice text as default if available (for manual input)
        voice_text = st.session_state.get("voice_text", "")
        if voice_text and st.session_state.voice_text and not st.session_state.get("auto_send_voice", False):
            default_prompt = voice_text
            st.session_state.voice_text = ""
        
        # Chat input
        attached_image = st.session_state.uploaded_image
        placeholder = "Message Code Gen AI..."
        if attached_image:
            placeholder = "Ask about this image..."
        
        user_prompt = st.chat_input(placeholder)
    
    with input_col2:
        if st.button("🎤", key="voice_btn_main", help="Voice input", use_container_width=True):
            st.session_state.show_voice_input = not st.session_state.show_voice_input
            st.session_state.show_image_upload = False
            st.rerun()
    
    with input_col3:
        if st.button("📷", key="img_btn_main", help="Upload an image", use_container_width=True):
            st.session_state.show_image_upload = not st.session_state.show_image_upload
            st.session_state.show_voice_input = False
            st.rerun()
    
    # Show image/voice upload sections below the input
    if st.session_state.show_image_upload:
        with st.container():
            uploaded_file = st.file_uploader(
                "Upload an image",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key="image_uploader",
                label_visibility="collapsed"
            )
            if uploaded_file:
                uploaded_image = Image.open(uploaded_file)
                st.session_state.uploaded_image = uploaded_image
                st.image(uploaded_image, width=200, caption="Ready to send")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ Keep", use_container_width=True):
                        st.session_state.show_image_upload = False
                        st.rerun()
                with col_b:
                    if st.button("✕ Remove", use_container_width=True):
                        st.session_state.uploaded_image = None
                        st.rerun()
    
    if st.session_state.show_voice_input:
        with st.container():
            st.info("🎤 Record your voice message (auto-transcription enabled)")
            
            audio_value = st.audio_input(
                "Record your message",
                key="audio_recorder",
                label_visibility="collapsed"
            )
            
            if audio_value:
                st.audio(audio_value)
                
                # Auto-transcribe when audio is recorded
                if audio_value and "last_audio_hash" not in st.session_state or st.session_state.get("last_audio_hash") != hash(audio_value.getvalue()):
                    st.session_state.last_audio_hash = hash(audio_value.getvalue())
                    
                    with st.spinner("🎙️ Auto-transcribing..."):
                        audio_bytes = audio_value.read()
                        
                        if SPEECH_RECOGNITION_AVAILABLE:
                            tmp_path = None
                            try:
                                import wave
                                import tempfile
                                import os
                                import time
                                
                                # Save to temp file for speech recognition
                                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                    tmp.write(audio_bytes)
                                    tmp_path = tmp.name
                                
                                # Ensure file is closed before using it
                                time.sleep(0.1)
                                
                                recognizer = sr.Recognizer()
                                with sr.AudioFile(tmp_path) as source:
                                    audio_data = recognizer.record(source)
                                
                                # Ensure AudioFile is closed before cleanup
                                voice_text = recognizer.recognize_google(audio_data)
                                st.session_state.voice_text = voice_text
                                st.session_state.auto_send_voice = True
                                
                                st.success(f"✅ Transcribed: {voice_text}")
                                st.info("💬 Sending to AI automatically...")
                                st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Transcription error: {e}")
                                st.session_state.voice_text = ""
                            finally:
                                # Clean up temp file with retry
                                if tmp_path and os.path.exists(tmp_path):
                                    for i in range(3):  # Try 3 times
                                        try:
                                            os.unlink(tmp_path)
                                            break
                                        except PermissionError:
                                            time.sleep(0.1)  # Wait a bit and retry
                                        except Exception:
                                            break  # Give up on other errors
                        else:
                            st.warning("⚠️ Install `SpeechRecognition` for auto-transcription: `pip install SpeechRecognition`")
                
                # Manual transcribe button as backup
                col_manual, col_clear = st.columns(2)
                with col_manual:
                    if st.button("🔄 Re-transcribe", use_container_width=True):
                        with st.spinner("🎙️ Transcribing..."):
                            audio_bytes = audio_value.read()
                            
                            if SPEECH_RECOGNITION_AVAILABLE:
                                tmp_path = None
                                try:
                                    import wave
                                    import tempfile
                                    import os
                                    import time
                                    
                                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                        tmp.write(audio_bytes)
                                        tmp_path = tmp.name
                                    
                                    # Ensure file is closed before using it
                                    time.sleep(0.1)
                                    
                                    recognizer = sr.Recognizer()
                                    with sr.AudioFile(tmp_path) as source:
                                        audio_data = recognizer.record(source)
                                    
                                    # Ensure AudioFile is closed before cleanup
                                    voice_text = recognizer.recognize_google(audio_data)
                                    st.session_state.voice_text = voice_text
                                    
                                    st.success(f"✅ Re-transcribed: {voice_text}")
                                except Exception as e:
                                    st.error(f"❌ Transcription error: {e}")
                                finally:
                                    # Clean up temp file with retry
                                    if tmp_path and os.path.exists(tmp_path):
                                        for i in range(3):  # Try 3 times
                                            try:
                                                os.unlink(tmp_path)
                                                break
                                            except PermissionError:
                                                time.sleep(0.1)  # Wait a bit and retry
                                            except Exception:
                                                break  # Give up on other errors
                
                with col_clear:
                    if st.button("🗑️ Clear", use_container_width=True):
                        st.session_state.voice_text = ""
                        if "last_audio_hash" in st.session_state:
                            del st.session_state.last_audio_hash
                        st.rerun()
    
    # Show pending image preview
    if st.session_state.uploaded_image and not st.session_state.show_image_upload:
        with st.container():
            col_img, col_remove = st.columns([4, 1])
            with col_img:
                st.image(st.session_state.uploaded_image, width=80)
            with col_remove:
                if st.button("✕", key="remove_preview"):
                    st.session_state.uploaded_image = None
                    st.rerun()
    
    # Handle auto-send voice input
    if st.session_state.get("auto_send_voice", False) and st.session_state.get("voice_text", ""):
        voice_prompt = st.session_state.voice_text
        st.session_state.voice_text = ""
        st.session_state.auto_send_voice = False
        st.session_state.show_voice_input = False
        
        handle_user_prompt(
            voice_prompt.strip(),
            mode,
            system_prompt.strip(),
            model,
            image=st.session_state.uploaded_image
        )
        st.rerun()
    
    if user_prompt:
        handle_user_prompt(
            user_prompt.strip(), 
            mode, 
            system_prompt.strip(), 
            model,
            image=st.session_state.uploaded_image
        )
        st.session_state.show_image_upload = False
        st.session_state.show_voice_input = False
        st.rerun()
    st.markdown('---')


if __name__ == "__main__":
    main()
