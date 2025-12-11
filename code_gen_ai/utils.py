"""Utility functions for Code Gen AI - TTS, transcription, image processing."""

import base64
import io
import re
from typing import Optional

import streamlit as st
from PIL import Image

# Audio processing imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def start_tts(text: str, message_index: int) -> None:
    """Start text-to-speech for the given text using browser's Web Speech API."""
    # Clean the text for TTS (remove markdown, code blocks, etc.)
    clean_text = re.sub(r'```[\s\S]*?```', 'code block omitted', text)
    clean_text = re.sub(r'`[^`]+`', '', clean_text)
    clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)
    clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)
    clean_text = re.sub(r'#{1,6}\s*', '', clean_text)
    clean_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_text)
    clean_text = clean_text.strip()
    
    st.session_state.tts_playing = True
    st.session_state.tts_message_index = message_index
    st.session_state.tts_text = clean_text
    
    # Use JavaScript Web Speech API for TTS
    js_code = f'''
    <script>
        const utterance = new SpeechSynthesisUtterance(`{clean_text.replace('`', '').replace('"', '\\"').replace("'", "\\'")[:2000]}`);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Try to use a good voice
        const voices = speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Microsoft'));
        if (preferredVoice) utterance.voice = preferredVoice;
        
        speechSynthesis.speak(utterance);
    </script>
    '''
    st.components.v1.html(js_code, height=0)


def stop_tts() -> None:
    """Stop text-to-speech playback."""
    st.session_state.tts_playing = False
    st.session_state.tts_message_index = None
    
    # Use JavaScript to stop speech
    js_code = '''
    <script>
        speechSynthesis.cancel();
    </script>
    '''
    st.components.v1.html(js_code, height=0)


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


def transcribe_audio_file(audio_value) -> Optional[str]:
    """Transcribe audio from a Streamlit audio input with proper file handling."""
    if not SPEECH_RECOGNITION_AVAILABLE:
        st.warning("⚠️ Install `SpeechRecognition` for auto-transcription: `pip install SpeechRecognition`")
        return None
    
    import tempfile
    import os
    import time
    
    tmp_path = None
    try:
        audio_bytes = audio_value.read()
        
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
        return voice_text
        
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
        return None
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
