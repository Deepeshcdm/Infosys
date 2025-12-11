"""CSS styles for Code Gen AI dark theme."""

import streamlit as st

CUSTOM_CSS = """
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
.message-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
    opacity: 0.7;
    transition: opacity 0.2s ease;
}
.message-actions:hover {
    opacity: 1;
}
.action-btn {
    background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%);
    border: 1px solid #3a3a3a;
    border-radius: 20px;
    padding: 0.35rem 0.75rem;
    color: #a0a0a0;
    font-size: 0.75rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    transition: all 0.2s ease;
}
.action-btn:hover {
    background: linear-gradient(145deg, #3a3a3a 0%, #2f2f2f 100%);
    border-color: #10a37f;
    color: #10a37f;
    transform: translateY(-1px);
}
.action-btn.playing {
    background: linear-gradient(145deg, #10a37f 0%, #0d8c6d 100%);
    border-color: #10a37f;
    color: #fff;
    animation: pulse-glow 1.5s infinite;
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(16, 163, 127, 0.3); }
    50% { box-shadow: 0 0 15px rgba(16, 163, 127, 0.6); }
}
.action-btn .icon {
    font-size: 0.85rem;
}
</style>
"""


def inject_custom_css() -> None:
    """Inject Code Gen AI-inspired dark theme styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
