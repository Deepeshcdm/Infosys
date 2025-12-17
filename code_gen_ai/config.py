"""Configuration constants and settings for Code Gen AI."""

import re
import os
from typing import Optional
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

# API Configuration
GROQ_BASE_URL_DIRECT = ""
GEMINI_API_KEY_DIRECT = ""
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"

# Chat Configuration
CHAT_MODES = ["Chat", "Generate Code", "Explain Code"]
MODEL_OPTIONS = ["gpt-oss-120b", "llama3", "deepseek-r1", "deepseek-ocr:3b"]
DEFAULT_SYSTEM_PROMPT = "You are ChatGPT, a large language model trained by OpenAI. You are helpful, creative, clever, and very friendly."

# Regex Patterns
CODE_BLOCK_PATTERN = re.compile(r"```(?P<lang>[\w+\-]*)\n(?P<code>.*?)```", re.DOTALL)

# Supported Image Types
SUPPORTED_IMAGE_TYPES = ["png", "jpg", "jpeg", "gif", "webp"]


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
