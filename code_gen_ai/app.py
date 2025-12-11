"""
Code Gen AI - Main Application Entry Point

A Streamlit ChatGPT-style frontend with image and voice input support.
Run with: streamlit run app.py
"""

import streamlit as st

from .styles import inject_custom_css
from .state import (
    init_session_state,
    get_active_messages,
    summarize_title,
)
from .backend import send_to_backend
from .components import (
    render_chat_history,
    render_sidebar,
    render_empty_state,
    render_input_area,
)


def handle_user_prompt(
    user_prompt: str, 
    mode: str, 
    system_prompt: str, 
    model: str,
    image=None
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


def main() -> None:
    """Main application entry point."""
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
    
    user_prompt = render_input_area()
    
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
    
    # Handle auto-send for enhanced buttons (Concept Explainer, Writing Generator, Bug Debugger)
    if st.session_state.get("auto_send_prompt", False) and st.session_state.get("pending_prompt", ""):
        pending_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = ""
        st.session_state.auto_send_prompt = False
        
        handle_user_prompt(
            pending_prompt.strip(),
            mode,
            system_prompt.strip(),
            model,
            image=st.session_state.uploaded_image
        )
        st.rerun()
    
    # Handle regenerate response
    if st.session_state.get("regenerate_index") is not None:
        regen_index = st.session_state.regenerate_index
        st.session_state.regenerate_index = None
        
        messages = get_active_messages()
        if regen_index > 0 and regen_index < len(messages):
            # Get the user message before this assistant response
            user_msg_index = regen_index - 1
            if messages[user_msg_index].get("role") == "user":
                user_prompt_regen = messages[user_msg_index].get("content", "")
                user_image_regen = messages[user_msg_index].get("image")
                
                # Remove the old assistant message
                messages.pop(regen_index)
                
                # Display existing messages
                render_chat_history(messages)
                
                # Generate new response with streaming
                with st.chat_message("assistant", avatar="✨"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in send_to_backend(
                        messages,
                        mode=mode,
                        system_prompt=system_prompt.strip(),
                        model=model,
                        image=user_image_regen,
                    ):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                
                messages.append({"role": "assistant", "content": full_response})
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
