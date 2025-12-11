"""Backend API integration for Code Gen AI - Groq, Ollama, and fallback responses."""

import json
from typing import Any, Dict, List, Optional

import requests
from PIL import Image

from .config import (
    OLLAMA_API_URL,
    GROQ_BASE_URL_DIRECT,
    get_secret_or_env,
)
from .utils import image_to_base64


def stream_generate(model: str, prompt: str, image: Optional[Image.Image] = None):
    """Stream generate response from Ollama API as a generator."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    if image is not None:
        encoded_image = image_to_base64(image)
        payload["image"] = {
            "name": "uploaded.png",
            "mime_type": "image/png",
            "data": encoded_image,
        }

    try:
        with requests.post(OLLAMA_API_URL, headers=headers, json=payload, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                
                line = raw_line.strip()
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
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
        yield f"[Error connecting to Ollama: {e}. Make sure Ollama is running locally.]"
    except Exception as e:
        yield f"[Ollama API error: {e}]"


def send_to_backend(
    messages: List[Dict[str, Any]],
    *,
    mode: str,
    system_prompt: str,
    model: str,
    image: Optional[Image.Image] = None,
):
    """Send messages to the selected backend model and yield assistant text chunks for streaming.

    Behavior:
    - If `model` == "gpt-oss-120b" use the Groq/OpenAI-compatible Responses API.
    - For llama3/deepseek-r1/qwen3-vl, uses Ollama API.
    - For other modes/models the function falls back to a friendly stub message.
    """

    user_prompt = next(
        (msg.get("content", "") for msg in reversed(messages) if msg.get("role") == "user"),
        "",
    )

    # If there is an image, attach a short descriptor to the prompt
    if image is not None:
        try:
            b64 = image_to_base64(image)
            user_prompt = f"[Image attached: base64_png({len(b64)} bytes)]\n\n" + user_prompt
        except Exception:
            user_prompt = "[Image attached]\n\n" + user_prompt

    if not user_prompt:
        yield "Hi there! Send a message or upload an image and I'll respond."
        return
    
    # Apply mode-specific instructions to the prompt
    mode_instructions = ""
    if mode == "Generate Code":
        mode_instructions = "You are a code generation assistant. Generate clean, efficient, and well-commented code based on the user's request. Always include code examples in your response.\n\n"
    elif mode == "Explain Code":
        mode_instructions = "You are a code explanation assistant. Provide clear, detailed explanations of code, breaking down how it works step by step. Explain concepts, logic flow, and best practices.\n\n"
    else:  # Chat mode
        mode_instructions = f"{system_prompt}\n\n"
    
    # Prepend mode instructions to user prompt
    full_prompt = mode_instructions + user_prompt

    # --------------------
    # Groq / OpenAI-compatible (gpt-oss-120b)
    # --------------------
    if model == "gpt-oss-120b":
        groq_api_key = get_secret_or_env("GROQ_API_KEY")
        # allow hardcoded fallback for convenience during local testing
        if not groq_api_key and "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":
            groq_api_key = "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".strip() or None

        groq_base = get_secret_or_env("GROQ_BASE_URL") or GROQ_BASE_URL_DIRECT or "https://api.groq.com/openai/v1"
        if not groq_api_key:
            yield "[GROQ API key not found. Set `GROQ_API_KEY` in Streamlit secrets, environment variables, or `GROQ_API_KEY_DIRECT` in this file.]"
            return

        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=groq_api_key,
                base_url=groq_base,
            )
            
            response = client.responses.create(
                input=full_prompt,
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
        except ImportError:
            yield "[OpenAI SDK not installed. Install: pip install openai]"
        except Exception as http_err:
            yield f"[Error calling Groq/OpenAI endpoint: {http_err}]"
        return

    # --------------------
    # Ollama Models (llama3, deepseek-r1, qwen3-vl:2b)
    # --------------------
    if model in ["llama3", "deepseek-r1", "qwen3-vl:2b"]:
        yield from stream_generate(model, full_prompt, image)
        return

    # --------------------
    # Mode-based helper behavior (existing helpful stubs)
    # --------------------
    if mode == "Generate Code":
        yield (
            f"Here's the code you requested! 🚀\n\n"
            "```python\n"
            "def solution(data):\n"
            '    """Generated based on your requirements."""\n'
            "    # Implementation goes here\n"
            "    result = process(data)\n"
            "    return result\n"
            "```\n\n"
            "**Key points:**\n"
            "- Clean and readable structure\n"
            "- Follows best practices\n"
            "- Ready to customize\n\n"
            "Would you like me to explain any part or make modifications?"
        )
        return

    if mode == "Explain Code":
        yield (
            "Let me break this down for you! 📚\n\n"
            "**Overview:**\n"
            "The code you shared performs a specific operation with clear logic.\n\n"
            "**Step-by-step explanation:**\n"
            "1. **Input handling** - Validates and processes input data\n"
            "2. **Core logic** - Performs the main computation\n"
            "3. **Output** - Returns the processed result\n\n"
            "**Complexity:** O(n) time, O(1) space\n\n"
            "Any questions about specific parts?"
        )
        return

    # Default fallback
    yield (
        f"Great question! Here's a friendly stub reply while the model call is not configured.\n\n"
        f"Your input: \"{user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}\"\n\n"
        f"Selected model: `{model}`\n"
        "To enable live responses, set API keys in Streamlit `secrets.toml` or environment variables and install the SDKs."
    )
