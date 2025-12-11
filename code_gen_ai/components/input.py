"""Input area components - text, voice, and image input."""

import os
import time
import tempfile
import streamlit as st
from PIL import Image

from ..utils import SPEECH_RECOGNITION_AVAILABLE

# Import speech recognition if available
if SPEECH_RECOGNITION_AVAILABLE:
    import speech_recognition as sr


def render_input_area():
    """Render the main input area with text, voice, and image buttons."""
    
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
        _render_image_upload()
    
    if st.session_state.show_voice_input:
        _render_voice_input()
    
    # Show pending image preview
    if st.session_state.uploaded_image and not st.session_state.show_image_upload:
        _render_image_preview()
    
    return user_prompt


def _render_image_upload():
    """Render the image upload section."""
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


def _render_voice_input():
    """Render the voice input section."""
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
                    _manual_transcribe(audio_value)
            
            with col_clear:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.voice_text = ""
                    if "last_audio_hash" in st.session_state:
                        del st.session_state.last_audio_hash
                    st.rerun()


def _manual_transcribe(audio_value):
    """Manually transcribe audio."""
    with st.spinner("🎙️ Transcribing..."):
        audio_bytes = audio_value.read()
        
        if SPEECH_RECOGNITION_AVAILABLE:
            tmp_path = None
            try:
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


def _render_image_preview():
    """Render the pending image preview."""
    with st.container():
        col_img, col_remove = st.columns([4, 1])
        with col_img:
            st.image(st.session_state.uploaded_image, width=80)
        with col_remove:
            if st.button("✕", key="remove_preview"):
                st.session_state.uploaded_image = None
                st.rerun()
