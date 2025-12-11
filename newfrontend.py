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

st.set_page_config(
    page_title="Code Gen AI",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Reset & Base Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    .stApp {
        background-color: #212121;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        max-width: 850px !important;
        padding-top: 1rem !important;
        padding-bottom: 100px !important;
        margin: 0 auto;
    }
    
    /* Custom Header */
    .chatgpt-header {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem 0;
        border-bottom: 1px solid #3d3d3d;
        margin-bottom: 1.5rem;
    }
    
    .chatgpt-header h1 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #ececec;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chatgpt-header .logo {
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Chat Container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        padding: 0 1rem;
        margin-bottom: 2rem;
    }
    
    /* Message Bubbles */
    .message-wrapper {
        display: flex;
        flex-direction: column;
        max-width: 100%;
    }
    
    .message-wrapper.user {
        align-items: flex-end;
    }
    
    .message-wrapper.assistant {
        align-items: flex-start;
    }
    
    .message-bubble {
        max-width: 85%;
        padding: 1rem 1.25rem;
        border-radius: 18px;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .message-bubble.user {
        background-color: #2f2f2f;
        color: #ececec;
        border-bottom-right-radius: 4px;
    }
    
    .message-bubble.assistant {
        background-color: #444654;
        color: #d1d5db;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .message-bubble pre {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
        margin: 0.5rem 0;
    }
    
    .message-bubble code {
        font-family: 'Fira Code', 'Consolas', monospace;
        font-size: 0.875rem;
    }
    
    /* Message Avatar */
    .message-avatar {
        width: 30px;
        height: 30px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        margin-bottom: 0.5rem;
    }
    
    .message-avatar.user {
        background-color: #5436DA;
        color: white;
    }
    
    .message-avatar.assistant {
        background-color: #10a37f;
        color: white;
    }
    
    /* Welcome Screen */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        text-align: center;
    }
    
    .welcome-logo {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    .welcome-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #ececec;
        margin-bottom: 0.75rem;
    }
    
    .welcome-subtitle {
        font-size: 1rem;
        color: #8e8ea0;
        max-width: 400px;
        line-height: 1.5;
    }
    
    /* Feature Pills */
    .feature-pills {
        display: flex;
        gap: 0.75rem;
        margin-top: 2rem;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .feature-pill {
        background-color: #2f2f2f;
        border: 1px solid #3d3d3d;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        color: #b4b4b4;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .feature-pill:hover {
        background-color: #3d3d3d;
        border-color: #4d4d4d;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2d2d2d;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }
    
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-header .logo {
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 12px;
    }
    
    .sidebar-header span {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ececec;
    }
    
    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 500;
        color: #8e8ea0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem 0.5rem;
        margin-top: 0.5rem;
    }
    
    /* Sidebar Buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: 1px solid #3d3d3d !important;
        border-radius: 8px !important;
        color: #ececec !important;
        font-size: 0.875rem !important;
        padding: 0.6rem 0.75rem !important;
        transition: all 0.15s ease !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2f2f2f !important;
        border-color: #4d4d4d !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #2f2f2f !important;
        border-color: #10a37f !important;
    }
    
    /* Chat List Items */
    .chat-list-item {
        display: flex;
        align-items: center;
        padding: 0.6rem 0.75rem;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.15s ease;
        color: #b4b4b4;
        font-size: 0.875rem;
        margin: 2px 0;
    }
    
    .chat-list-item:hover {
        background-color: #2f2f2f;
    }
    
    .chat-list-item.active {
        background-color: #2f2f2f;
        color: #ececec;
    }
    
    /* Input Area Styling */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 850px;
        padding: 1rem 1.5rem 1.5rem;
        background: linear-gradient(to top, #212121 85%, transparent);
        z-index: 1000;
    }
    
    .input-wrapper {
        background-color: #2f2f2f;
        border: 1px solid #3d3d3d;
        border-radius: 16px;
        padding: 0.75rem 1rem;
        display: flex;
        align-items: flex-end;
        gap: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    
    .input-wrapper:focus-within {
        border-color: #10a37f;
        box-shadow: 0 0 0 2px rgba(16,163,127,0.1), 0 2px 8px rgba(0,0,0,0.15);
    }
    
    /* Streamlit text area customization */
    .stTextArea textarea {
        background-color: transparent !important;
        border: none !important;
        color: #ececec !important;
        font-size: 0.95rem !important;
        resize: none !important;
        padding: 0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stTextArea textarea:focus {
        box-shadow: none !important;
    }
    
    .stTextArea label {
        display: none !important;
    }
    
    /* Send Button */
    .send-button {
        background-color: #10a37f;
        border: none;
        border-radius: 8px;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.15s ease;
        flex-shrink: 0;
    }
    
    .send-button:hover {
        background-color: #1a7f64;
    }
    
    .send-button:disabled {
        background-color: #3d3d3d;
        cursor: not-allowed;
    }
    
    /* Input icons */
    .input-icons {
        display: flex;
        gap: 0.5rem;
        color: #8e8ea0;
    }
    
    .input-icon {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.15s ease;
    }
    
    .input-icon:hover {
        background-color: #3d3d3d;
    }
    
    /* Mode Toggle */
    .mode-toggle {
        display: flex;
        background-color: #2f2f2f;
        border-radius: 10px;
        padding: 4px;
        margin-bottom: 1rem;
    }
    
    .mode-option {
        flex: 1;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        color: #8e8ea0;
        cursor: pointer;
        text-align: center;
        transition: all 0.15s ease;
    }
    
    .mode-option.active {
        background-color: #10a37f;
        color: white;
    }
    
    /* Temp chat banner */
    .temp-banner {
        background-color: #2f2f2f;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        font-size: 0.8rem;
        color: #fbbf24;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Search Input */
    .stTextInput input {
        background-color: #2f2f2f !important;
        border: 1px solid #3d3d3d !important;
        border-radius: 8px !important;
        color: #ececec !important;
        font-size: 0.875rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #10a37f !important;
        box-shadow: none !important;
    }
    
    .stTextInput label {
        color: #8e8ea0 !important;
        font-size: 0.75rem !important;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background-color: #2f2f2f !important;
        border: 1px solid #3d3d3d !important;
        border-radius: 8px !important;
        color: #ececec !important;
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        color: #b4b4b4 !important;
    }
    
    /* Divider */
    hr {
        border-color: #2d2d2d !important;
        margin: 0.75rem 0 !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #2f2f2f;
        border: 1px dashed #3d3d3d;
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .stFileUploader label {
        color: #8e8ea0 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #2f2f2f;
        border-radius: 10px;
        padding: 4px;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8e8ea0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #10a37f !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3d3d3d;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4d4d4d;
    }
    
    /* Info/Warning boxes */
    .stAlert {
        background-color: #2f2f2f !important;
        border: 1px solid #3d3d3d !important;
        border-radius: 8px !important;
        color: #b4b4b4 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #10a37f !important;
    }
    
    /* Chat message override */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }
    
    [data-testid="stChatMessageContent"] {
        background-color: #444654 !important;
        border-radius: 18px !important;
        padding: 1rem 1.25rem !important;
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] {
        color: #d1d5db !important;
    }
    
    /* User message specific */
    [data-testid="stChatMessage"][data-testid-kind="user"] [data-testid="stChatMessageContent"] {
        background-color: #2f2f2f !important;
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
    for chat_id in list(st.session_state.selected_chats):
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
    try:
        client = OpenAI(
            api_key="key",
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
    if feature_mode == "Code Generation":
        enhanced_prompt = f"""You are an expert code generator. Generate clean, well-documented, and efficient code based on the following request. Include comments explaining the code.

Request: {prompt}

Please provide the code with proper formatting and explanations."""
    else:
        enhanced_prompt = f"""You are an expert code explainer. Analyze and explain the following code in detail. Break down the logic, explain what each part does, and highlight any important concepts or patterns used.

Code/Question: {prompt}

Please provide a comprehensive explanation."""

    if model == "gpt-oss-120b":
        return stream_generate_groq(enhanced_prompt)
    else:
        return stream_generate_ollama(model, enhanced_prompt)


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


with st.sidebar:
    # Sidebar header
    st.markdown("""
    <div class="sidebar-header">
        <div class="logo">C</div>
        <span>Code Gen AI</span>
    </div>
    """, unsafe_allow_html=True)
    
    # New Chat button
    if st.button("+ New chat", use_container_width=True):
        create_new_chat(is_temporary=False)
        st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Temporary", use_container_width=True, help="Chat won't be saved"):
            create_new_chat(is_temporary=True)
            st.rerun()
    with col2:
        if st.button("Clear", use_container_width=True):
            clear_current_chat()
            st.rerun()
    
    st.divider()
    
    # Search
    search_query = st.text_input("Search chats", value=st.session_state.search_query, placeholder="Search...", label_visibility="collapsed")
    st.session_state.search_query = search_query
    
    # Delete selected button
    if len(st.session_state.selected_chats) > 0:
        if st.button(f"Delete selected ({len(st.session_state.selected_chats)})", use_container_width=True):
            delete_selected_chats()
            st.rerun()
    
    st.markdown('<div class="sidebar-section-title">Previous Chats</div>', unsafe_allow_html=True)
    
    filtered_chats = filter_chats(search_query)
    
    if filtered_chats:
        for chat_id, chat_data in sorted(filtered_chats.items(), key=lambda x: x[1]["created_at"], reverse=True):
            col1, col2 = st.columns([0.12, 0.88])
            
            with col1:
                is_selected = chat_id in st.session_state.selected_chats
                if st.checkbox("", value=is_selected, key=f"select_{chat_id}", label_visibility="collapsed"):
                    st.session_state.selected_chats.add(chat_id)
                else:
                    st.session_state.selected_chats.discard(chat_id)
            
            with col2:
                is_current = chat_id == st.session_state.current_chat_id
                button_type = "primary" if is_current else "secondary"
                icon = "◆" if chat_data.get("feature_mode") == "Code Generation" else "◇"
                
                if st.button(
                    f"{icon} {chat_data['title'][:22]}",
                    key=f"chat_{chat_id}",
                    use_container_width=True,
                    type=button_type
                ):
                    save_current_chat()
                    load_chat(chat_id)
                    st.rerun()
    else:
        st.markdown('<p style="color: #8e8ea0; font-size: 0.85rem; padding: 0.5rem;">No chats yet</p>', unsafe_allow_html=True)
    
    # Temp chat indicator
    if st.session_state.is_temporary:
        st.markdown("""
        <div class="temp-banner">
            <span>⚡</span> Temporary chat - won't be saved
        </div>
        """, unsafe_allow_html=True)


# Header
st.markdown("""
<div class="chatgpt-header">
    <h1><div class="logo">C</div> Code Gen AI</h1>
</div>
""", unsafe_allow_html=True)

# Mode and Model Selection
col1, col2 = st.columns(2)

with col1:
    feature_mode = st.selectbox(
        "Mode",
        ["Code Generation", "Code Explanation"],
        index=0 if st.session_state.feature_mode == "Code Generation" else 1,
        label_visibility="collapsed"
    )
    st.session_state.feature_mode = feature_mode

with col2:
    selected_model = st.selectbox(
        "Model",
        MODEL_OPTIONS,
        label_visibility="collapsed"
    )

# Chat display area
if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome-container">
        <div class="welcome-logo">C</div>
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-subtitle">
            {"Describe what you want to build, and I'll generate the code for you." if feature_mode == "Code Generation" else "Paste your code or ask questions, and I'll explain it in detail."}
        </div>
        <div class="feature-pills">
            <div class="feature-pill">Generate a Python function</div>
            <div class="feature-pill">Create a REST API</div>
            <div class="feature-pill">Build a React component</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="✦"):
                st.markdown(message["content"])

st.divider()

input_tab1, input_tab2, input_tab3 = st.tabs(["Text", "Image", "Voice"])

user_input = None

with input_tab1:
    placeholder_text = "Describe the code you want to generate..." if feature_mode == "Code Generation" else "Paste code to explain or ask a question..."
    
    text_input = st.text_area(
        "Message",
        placeholder=placeholder_text,
        height=100,
        label_visibility="collapsed",
        key="text_input"
    )
    
    if st.button("Send", use_container_width=True, type="primary", key="send_text"):
        if text_input.strip():
            user_input = text_input

with input_tab2:
    uploaded_image = st.file_uploader(
        "Upload code screenshot or diagram",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        label_visibility="collapsed"
    )
    
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, use_container_width=True)
        
        image_description = st.text_input(
            "Context",
            placeholder="Describe what you want to know...",
            label_visibility="collapsed"
        )
        
        if st.button("Analyze", use_container_width=True, type="primary", key="send_image"):
            if feature_mode == "Code Generation":
                user_input = f"[Image uploaded] {image_description if image_description else 'Generate code based on this image'}"
            else:
                user_input = f"[Image uploaded] {image_description if image_description else 'Explain the code in this image'}"

with input_tab3:
    st.markdown("""
    <p style="color: #8e8ea0; font-size: 0.875rem; margin-bottom: 1rem;">
        Click to start recording, speak your prompt, then copy the result to the Text tab.
    </p>
    """, unsafe_allow_html=True)
    
    voice_html = """
    <div style="padding: 1rem; background: #2f2f2f; border-radius: 12px; border: 1px solid #3d3d3d;">
        <button id="voiceBtn" onclick="startVoice()" style="
            background: #10a37f;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        ">
            🎤 Start Recording
        </button>
        <p id="status" style="text-align: center; margin-top: 0.75rem; color: #8e8ea0; font-size: 0.85rem;"></p>
        <textarea id="result" style="
            width: 100%;
            min-height: 60px;
            margin-top: 0.75rem;
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid #3d3d3d;
            background: #212121;
            color: #ececec;
            font-size: 0.9rem;
            display: none;
            resize: none;
        "></textarea>
    </div>
    
    <script>
        function startVoice() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                document.getElementById('status').innerText = 'Not supported in this browser';
                return;
            }
            
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SR();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            const btn = document.getElementById('voiceBtn');
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            
            btn.innerHTML = '🔴 Recording...';
            btn.style.background = '#ef4444';
            status.innerText = 'Listening...';
            
            recognition.onresult = function(e) {
                let t = '';
                for (let i = 0; i < e.results.length; i++) t += e.results[i][0].transcript;
                result.value = t;
                result.style.display = 'block';
            };
            
            recognition.onend = function() {
                btn.innerHTML = '🎤 Start Recording';
                btn.style.background = '#10a37f';
                status.innerText = 'Done! Copy the text above.';
            };
            
            recognition.onerror = function(e) {
                btn.innerHTML = '🎤 Start Recording';
                btn.style.background = '#10a37f';
                status.innerText = 'Error: ' + e.error;
            };
            
            recognition.start();
        }
    </script>
    """
    st.components.v1.html(voice_html, height=200)

# Process input
if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    with st.chat_message("assistant", avatar="✦"):
        response_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Thinking..."):
            try:
                for chunk in generate_response(user_input, selected_model, feature_mode):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {str(e)}"
                response_placeholder.error(full_response)
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
    
    save_current_chat()
    st.rerun()
