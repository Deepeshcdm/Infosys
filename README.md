# ChatGPT-Style Code Companion

A Streamlit-only frontend that mimics ChatGPT for code generation and explanation. It keeps the entire conversation in `st.session_state`, offers a sidebar with mode/model/system prompt controls, and exposes a single stub function (`send_to_backend`) where you can later connect Ollama or any other LLM provider.

## Features

- Dark ChatGPT-inspired layout with hero welcome card and message bubbles
- Sidebar controls for mode selection, placeholder model selector, system prompt, and display name
- Chat history stored entirely on the client via `st.session_state`
- Markdown + fenced code block rendering for assistant replies
- One-click conversation reset
- Drop-in backend stub ready to be replaced with an Ollama/OpenAI call

## Project Structure

```
FrontEnd.py   # Full Streamlit UI
app.py        # Thin wrapper so `streamlit run app.py` works
README.md     # This file
requirements.txt
```

## Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Hooking Up Ollama (or any LLM)

1. Ensure you have Ollama running locally (default: `http://127.0.0.1:11434`).
2. Configure the host via the "Ollama host" field in the sidebar (or set the `OLLAMA_HOST` env var).
3. The app already calls Ollama via `/api/chat/completions`, so just keep the UI running.

That's it—the rest of the UI already behaves like ChatGPT, so once you swap in your backend this becomes a fully working chat assistant for code.
