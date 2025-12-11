"""Sidebar UI components."""

import streamlit as st

from ..config import CHAT_MODES, MODEL_OPTIONS, DEFAULT_SYSTEM_PROMPT
from ..state import (
    delete_chat,
    rename_chat,
    clear_conversation,
    handle_new_chat_button,
    ensure_current_chat,
    search_in_chat,
)


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


def render_sidebar() -> tuple:
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
