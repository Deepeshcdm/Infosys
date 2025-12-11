"""Session state management for Code Gen AI."""

from typing import Any, Dict, List, Optional
import streamlit as st

from .config import CHAT_MODES, MODEL_OPTIONS, DEFAULT_SYSTEM_PROMPT


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
    # Feature toggles for enhanced buttons
    st.session_state.setdefault("concept_difficulty", "Intermediate")
    st.session_state.setdefault("writing_tone", "Formal")
    st.session_state.setdefault("show_concept_explainer", False)
    st.session_state.setdefault("show_writing_generator", False)
    st.session_state.setdefault("show_bug_debugger", False)
    st.session_state.setdefault("current_concept", None)
    st.session_state.setdefault("current_writing_task", None)
    st.session_state.setdefault("current_bug", None)
    st.session_state.setdefault("auto_send_prompt", False)
    st.session_state.setdefault("pending_prompt", "")
    st.session_state.setdefault("regenerate_index", None)
    st.session_state.setdefault("tts_playing", False)
    st.session_state.setdefault("tts_message_index", None)

    ensure_current_chat()


def get_active_messages() -> List[Dict[str, Any]]:
    """Return the list that represents the active conversation."""
    if st.session_state.is_temp_chat:
        return st.session_state.temp_messages
    return st.session_state.chats[st.session_state.current_chat_id]["messages"]


def set_sidebar_notice(message: str) -> None:
    """Store a short notice message for sidebar alerts."""
    st.session_state.sidebar_notice = message


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


def search_in_chat(chat_id: str, query: str) -> tuple:
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
