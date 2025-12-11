import streamlit as st
import json
from datetime import datetime
import time
import random

# Page configuration
st.set_page_config(
    page_title="ChatGPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS - Complete ChatGPT Clone Styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root Variables - ChatGPT Dark Theme */
    :root {
        --bg-primary: #212121;
        --bg-secondary: #2f2f2f;
        --bg-tertiary: #171717;
        --bg-sidebar: #171717;
        --text-primary: #ececec;
        --text-secondary: #b4b4b4;
        --text-muted: #8e8e8e;
        --accent-green: #10a37f;
        --accent-hover: #1a7f64;
        --border-color: #2f2f2f;
        --user-msg-bg: #2f2f2f;
        --input-bg: #2f2f2f;
        --hover-bg: #424242;
        --scrollbar-thumb: #565656;
    }
    
    /* Global Styles */
    .stApp {
        background-color: var(--bg-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--scrollbar-thumb);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #6e6e6e;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: var(--bg-sidebar) !important;
        padding-top: 0 !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        width: 260px !important;
    }
    
    /* Sidebar content */
    .sidebar-section {
        padding: 12px 16px 8px;
        font-size: 12px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Override Streamlit Button in sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: var(--hover-bg) !important;
        border-color: #4f4f4f !important;
    }
    
    /* Welcome Container */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 20px 40px;
        text-align: center;
    }
    
    .welcome-logo {
        width: 72px;
        height: 72px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 40px;
    }
    
    /* Suggestion Cards */
    .suggestion-card {
        background-color: transparent;
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        min-height: 80px;
    }
    
    .suggestion-card:hover {
        background-color: var(--hover-bg);
        border-color: #4f4f4f;
    }
    
    .suggestion-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    
    .suggestion-desc {
        font-size: 13px;
        color: var(--text-muted);
        line-height: 1.4;
    }
    
    /* Chat Messages */
    .message-wrapper {
        padding: 24px 0;
        max-width: 768px;
        margin: 0 auto;
    }
    
    .message-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    
    .message-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #ae65c5 0%, #8b5fc7 100%);
        color: white;
    }
    
    .assistant-avatar {
        background-color: #19c37d;
        color: white;
    }
    
    .message-author {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .message-content {
        font-size: 16px;
        line-height: 1.75;
        color: var(--text-primary);
        padding-left: 42px;
    }
    
    /* Message Actions */
    .message-actions {
        display: flex;
        gap: 2px;
        padding-left: 42px;
        margin-top: 16px;
    }
    
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 6px;
        background: transparent;
        color: var(--text-muted);
        cursor: pointer;
        transition: all 0.15s ease;
        border: none;
        font-size: 14px;
    }
    
    .action-btn:hover {
        background-color: var(--hover-bg);
        color: var(--text-primary);
    }
    
    /* Chat Input Container */
    .chat-input-wrapper {
        max-width: 768px;
        margin: 0 auto;
        padding: 0 16px;
    }
    
    .input-container {
        background-color: var(--input-bg);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .input-container:focus-within {
        border-color: #4f4f4f;
    }
    
    /* Override Streamlit Text Input */
    .stTextInput > div > div > input {
        background-color: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        font-size: 16px !important;
        padding: 8px 0 !important;
    }
    
    .stTextInput > div > div > input:focus {
        box-shadow: none !important;
        border: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    .stTextInput > label {
        display: none !important;
    }
    
    .stTextInput > div {
        border: none !important;
        background: transparent !important;
    }
    
    .stTextInput > div > div {
        border: none !important;
        background: transparent !important;
    }
    
    /* Footer Text */
    .footer-text {
        text-align: center;
        font-size: 12px;
        color: var(--text-muted);
        padding: 12px 0 24px;
    }
    
    /* Override Streamlit Button in main area */
    .stButton > button {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background-color: var(--hover-bg) !important;
        border-color: #4f4f4f !important;
    }
    
    /* Select Box Styling */
    .stSelectbox > div > div {
        background-color: transparent !important;
        border: none !important;
    }
    
    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }
    
    .stSelectbox svg {
        fill: var(--text-primary) !important;
    }
    
    [data-baseweb="select"] {
        background-color: transparent !important;
    }
    
    [data-baseweb="select"] > div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Remove Streamlit Padding */
    .block-container {
        padding: 0 !important;
        max-width: none !important;
    }
    
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: var(--text-primary) !important;
    }
    
    /* User Profile in sidebar */
    .user-profile {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 10px;
        cursor: pointer;
    }
    
    .user-profile:hover {
        background-color: var(--hover-bg);
    }
    
    .user-avatar-small {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ae65c5 0%, #8b5fc7 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Custom send button */
    .send-button {
        background-color: white !important;
        color: #212121 !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
        cursor: pointer !important;
        padding: 0 !important;
        min-width: 32px !important;
    }
    
    .send-button:hover {
        background-color: #e0e0e0 !important;
    }
    
    /* OpenAI Logo styling */
    .openai-logo {
        color: white;
    }
    
    /* Horizontal rule styling */
    hr {
        border-color: var(--border-color) !important;
        margin: 8px 0 !important;
    }
    
    /* Code blocks */
    code {
        background-color: #1e1e1e !important;
        color: #e6e6e6 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    
    pre {
        background-color: #1e1e1e !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_model' not in st.session_state:
    st.session_state.current_model = "ChatGPT 4o"

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"id": 1, "title": "New chat", "date": "Today"},
    ]

if 'selected_chat' not in st.session_state:
    st.session_state.selected_chat = 0

# OpenAI SVG Logo
openai_logo_svg = """
<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.8956zm16.0993 3.8558L12.6 8.3829l2.02-1.1638a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z" fill="#fff"/>
</svg>
"""

# Sidebar
with st.sidebar:
    # Logo and New Chat
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 8px 16px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            {openai_logo_svg}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("✏️  New chat", key="new_chat", use_container_width=True):
        st.session_state.messages = []
        new_chat = {"id": len(st.session_state.chat_history) + 1, "title": "New chat", "date": "Today"}
        st.session_state.chat_history.insert(0, new_chat)
        st.session_state.selected_chat = 0
        st.rerun()
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # Chat History
    st.markdown("<div class='sidebar-section'>Recent</div>", unsafe_allow_html=True)
    
    for idx, chat in enumerate(st.session_state.chat_history[:7]):
        chat_title = chat['title'][:28] + '...' if len(chat['title']) > 28 else chat['title']
        if st.button(f"💬 {chat_title}", key=f"chat_{idx}", use_container_width=True):
            st.session_state.selected_chat = idx
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Explore Section
    st.markdown("<div class='sidebar-section'>Explore</div>", unsafe_allow_html=True)
    
    if st.button("🔍 Explore GPTs", key="explore_gpts", use_container_width=True):
        st.toast("Opening GPT Store...")
    
    if st.button("🎨 DALL·E", key="dalle", use_container_width=True):
        st.toast("Opening DALL·E...")
    
    # Spacer
    st.markdown("<div style='flex: 1; min-height: 100px;'></div>", unsafe_allow_html=True)
    
    # User Profile at bottom
    st.markdown("---")
    st.markdown("""
    <div class="user-profile">
        <div class="user-avatar-small">U</div>
        <span style="font-size: 14px; color: #ececec; font-weight: 500;">User</span>
    </div>
    """, unsafe_allow_html=True)

# Main Content
main_col1, main_col2, main_col3 = st.columns([0.5, 5, 0.5])

with main_col2:
    # Header with model selector
    header_col1, header_col2 = st.columns([4, 2])
    
    with header_col1:
        model = st.selectbox(
            "model_select",
            ["ChatGPT 4o", "ChatGPT 4o mini", "ChatGPT 4", "ChatGPT 3.5"],
            index=0,
            label_visibility="collapsed"
        )
        st.session_state.current_model = model
    
    with header_col2:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col2:
            if st.button("↗️ Share", key="share_btn"):
                st.toast("Share link copied!")
    
    # Content Area
    if len(st.session_state.messages) == 0:
        # Welcome Screen
        st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-logo">
                {openai_logo_svg.replace('width="28"', 'width="48"').replace('height="28"', 'height="48"')}
            </div>
            <div class="welcome-title">How can I help you today?</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Suggestion Cards
        st.markdown("<div style='max-width: 680px; margin: 0 auto; padding: 0 20px;'>", unsafe_allow_html=True)
        
        card_col1, card_col2 = st.columns(2)
        
        with card_col1:
            st.markdown("""
            <div class="suggestion-card">
                <div class="suggestion-title">✏️ Create image</div>
                <div class="suggestion-desc">Generate an image for a presentation or social media</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="suggestion-card">
                <div class="suggestion-title">📝 Summarize text</div>
                <div class="suggestion-desc">Condense long articles or documents into key points</div>
            </div>
            """, unsafe_allow_html=True)
        
        with card_col2:
            st.markdown("""
            <div class="suggestion-card">
                <div class="suggestion-title">💻 Help me with code</div>
                <div class="suggestion-desc">Debug, explain, or write code in any language</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="suggestion-card">
                <div class="suggestion-title">💡 Brainstorm ideas</div>
                <div class="suggestion-desc">Generate creative concepts for any project</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Display Chat Messages
        for idx, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-wrapper">
                    <div class="message-header">
                        <div class="message-avatar user-avatar">U</div>
                        <div class="message-author">You</div>
                    </div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-wrapper">
                    <div class="message-header">
                        <div class="message-avatar assistant-avatar">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                                <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729z" fill="#fff"/>
                            </svg>
                        </div>
                        <div class="message-author">ChatGPT</div>
                    </div>
                    <div class="message-content">{message["content"]}</div>
                    <div class="message-actions">
                        <span class="action-btn" title="Read aloud">🔊</span>
                        <span class="action-btn" title="Copy">📋</span>
                        <span class="action-btn" title="Good response">👍</span>
                        <span class="action-btn" title="Bad response">👎</span>
                        <span class="action-btn" title="Regenerate">🔄</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Spacing before input
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    
    # Chat Input Area
    st.markdown("<div class='chat-input-wrapper'>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="input-container">
    """, unsafe_allow_html=True)
    
    input_col1, input_col2, input_col3 = st.columns([1, 12, 1])
    
    with input_col1:
        st.markdown("<div style='padding: 8px; color: #8e8e8e; font-size: 18px; cursor: pointer;'>📎</div>", unsafe_allow_html=True)
    
    with input_col2:
        user_input = st.text_input(
            "Message",
            key="user_input",
            placeholder="Message ChatGPT",
            label_visibility="collapsed"
        )
    
    with input_col3:
        send_clicked = st.button("⬆️", key="send_btn", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer-text">
        ChatGPT can make mistakes. Check important info.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Handle message sending
if (send_clicked and user_input) or (user_input and st.session_state.get('last_input') != user_input):
    st.session_state.last_input = user_input
    
    if user_input.strip():
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate demo response
        responses = [
            f"""I'd be happy to help you with that!

Based on your message about **"{user_input}"**, here's what I can tell you:

This is a demonstration of the ChatGPT UI clone built with Streamlit. In a production environment, this would connect to the actual OpenAI API.

**Key features of this interface:**
- 🎨 Authentic dark theme styling
- 💬 Chat history management  
- 🔄 Model selection
- ✨ Smooth user experience

Is there anything specific you'd like me to help you explore?""",
            
            f"""Great question! Let me help you with **"{user_input}"**.

This Streamlit application replicates the ChatGPT experience with careful attention to:

1. **Visual Design** - Matching OpenAI's color palette and typography
2. **User Interface** - Sidebar navigation, model selector, and chat layout
3. **Interactions** - Message history, action buttons, and responsive design

Feel free to ask me anything else!""",
        ]
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": random.choice(responses),
            "timestamp": datetime.now().isoformat()
        })
        
        # Update chat title
        if len(st.session_state.messages) == 2:
            st.session_state.chat_history[st.session_state.selected_chat]["title"] = user_input[:30]
        
        st.rerun()
