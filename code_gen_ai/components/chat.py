"""Chat history and message rendering components."""

import base64
from io import BytesIO
from typing import Any, Dict, List
import streamlit as st
from PIL import Image

from ..config import CODE_BLOCK_PATTERN
from ..utils import start_tts, stop_tts


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
    for idx, message in enumerate(messages):
        role = message.get("role", "assistant")
        avatar = "👤" if role == "user" else "✨"
        
        # Create unique key suffix using index and content hash
        content_hash = hash(message.get("content", ""))
        unique_key = f"{idx}_{content_hash}_{role}"
        
        with st.chat_message(role, avatar=avatar):
            # Show image if present in message (from base64 or PIL Image)
            if "image_base64" in message and message["image_base64"]:
                # Decode base64 image
                image_data = base64.b64decode(message["image_base64"])
                image = Image.open(BytesIO(image_data))
                st.image(image, width=300)
            elif "image" in message and message["image"]:
                # Backward compatibility for PIL Images
                st.image(message["image"], width=300)
            
            st.markdown(f"<div class='chat-bubble'>", unsafe_allow_html=True)
            parse_and_render_segments(message.get("content", ""))
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add action buttons for assistant messages
            if role == "assistant" and message.get("content"):
                btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 5])
                
                with btn_col1:
                    is_playing = st.session_state.get("tts_playing") and st.session_state.get("tts_message_index") == idx
                    if st.button(
                        "🔊 Read" if not is_playing else "⏹️ Stop",
                        key=f"tts_btn_{unique_key}",
                        help="Read this response aloud",
                        use_container_width=True
                    ):
                        if is_playing:
                            stop_tts()
                        else:
                            start_tts(message.get("content", ""), idx)
                
                with btn_col2:
                    if st.button(
                        "🔄 Redo",
                        key=f"regen_btn_{unique_key}",
                        help="Regenerate this response",
                        use_container_width=True
                    ):
                        st.session_state.regenerate_index = idx
                        st.rerun()
                
                with btn_col3:
                    if st.button(
                        "📋 Copy",
                        key=f"copy_btn_{unique_key}",
                        help="Copy to clipboard",
                        use_container_width=True
                    ):
                        st.session_state[f"show_copy_{idx}"] = True
                        st.rerun()
                
                # Show copy modal with text area for easy copying
                if st.session_state.get(f"show_copy_{idx}", False):
                    with st.expander("📋 Copy Text", expanded=True):
                        content_to_copy = message.get("content", "")
                        st.text_area(
                            "Select all (Ctrl+A) and copy (Ctrl+C):",
                            value=content_to_copy,
                            height=200,
                            key=f"copy_area_{idx}",
                            label_visibility="visible"
                        )
                        
                        col_close, col_download = st.columns(2)
                        with col_close:
                            if st.button("✕ Close", key=f"close_copy_{idx}", use_container_width=True):
                                st.session_state[f"show_copy_{idx}"] = False
                                st.rerun()
                        with col_download:
                            st.download_button(
                                "💾 Download",
                                data=content_to_copy,
                                file_name="response.txt",
                                mime="text/plain",
                                key=f"download_{idx}",
                                use_container_width=True
                            )
                        
                        # JavaScript to auto-select text
                        st.components.v1.html(
                            f"""
                            <script>
                                setTimeout(function() {{
                                    const textarea = window.parent.document.querySelector('textarea[aria-label="Select all (Ctrl+A) and copy (Ctrl+C):"]');
                                    if (textarea) {{
                                        textarea.select();
                                        textarea.focus();
                                    }}
                                }}, 100);
                            </script>
                            """,
                            height=0
                        )
