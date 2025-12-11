"""Empty state / hero section and suggestion cards."""

import random
import streamlit as st

from ..config import CHAT_MODES, MODEL_OPTIONS
from ..data import CONCEPTS_BY_DIFFICULTY, WRITING_TASKS_BY_TONE, BUGGY_CODE_SNIPPETS


def set_empty_state_action(prefill_text: str, *, show_image_upload: bool = False) -> None:
    """Apply suggestion card action and optionally open the image uploader."""
    st.session_state.prefill_prompt = prefill_text
    if show_image_upload:
        st.session_state.show_image_upload = True
        st.session_state.show_voice_input = False


def trigger_concept_explainer() -> None:
    """Trigger the random concept explainer feature."""
    st.session_state.show_concept_explainer = True
    st.session_state.show_writing_generator = False
    st.session_state.show_bug_debugger = False
    difficulty = st.session_state.get("concept_difficulty", "Intermediate")
    concepts = CONCEPTS_BY_DIFFICULTY.get(difficulty, CONCEPTS_BY_DIFFICULTY["Intermediate"])
    st.session_state.current_concept = random.choice(concepts)


def trigger_writing_generator() -> None:
    """Trigger the random writing generator feature."""
    st.session_state.show_writing_generator = True
    st.session_state.show_concept_explainer = False
    st.session_state.show_bug_debugger = False
    tone = st.session_state.get("writing_tone", "Formal")
    tasks = WRITING_TASKS_BY_TONE.get(tone, WRITING_TASKS_BY_TONE["Formal"])
    st.session_state.current_writing_task = random.choice(tasks)


def trigger_bug_debugger() -> None:
    """Trigger the random bug debugger feature."""
    st.session_state.show_bug_debugger = True
    st.session_state.show_concept_explainer = False
    st.session_state.show_writing_generator = False
    st.session_state.current_bug = random.choice(BUGGY_CODE_SNIPPETS)


def generate_concept_prompt(concept: dict, difficulty: str) -> str:
    """Generate a prompt for the AI to explain a concept."""
    return f"""Explain the concept of "{concept['topic']}" from the category "{concept['category']}" at a {difficulty} level.

Please provide:
1. **Simple Explanation** (2-3 sentences for beginners)
2. **Structured Explanation** (detailed breakdown with key points)
3. **Real-World Analogy** (relatable comparison)
4. **Interview Question** (one common interview question on this topic with a brief answer)

Make sure to adjust the complexity based on the {difficulty} level."""


def generate_writing_prompt(task: dict, tone: str) -> str:
    """Generate a prompt for the AI to create writing content."""
    return f"""Generate a {tone.lower()} {task['type'].lower()} with the following task:

"{task['prompt']}"

Please create a complete, well-written piece that matches the {tone.lower()} tone. Include proper formatting and structure appropriate for a {task['type']}."""


def generate_bug_prompt(bug: dict) -> str:
    """Generate a prompt for the bug debugger feature."""
    return f"""I'm practicing debugging! Here's a buggy {bug['language']} code snippet:

**Bug Title:** {bug['title']}

```{bug['language']}
{bug['buggy_code']}
```

Please analyze this code and provide:
1. **What's wrong?** - Identify the bug
2. **Fixed Code** - Show the corrected version
3. **Explanation** - Why did this bug occur?
4. **Prevention Tips** - How to avoid this in the future

Help me understand this debugging challenge!"""


def render_empty_state(display_name: str) -> None:
    """Stunning ChatGPT-style welcome screen with animated suggestions and interactive features."""
    
    # Get current model for display
    current_model = st.session_state.get("model_select", MODEL_OPTIONS[0])
    current_mode = st.session_state.get("mode_select", CHAT_MODES[0])
    
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-glow"></div>
            <div class="hero-logo">✨</div>
            <div class="hero-title">Hi {display_name}, how can I help?</div>
            <div class="hero-subtitle">
                I'm your AI coding assistant. Ask me anything, upload an image for analysis,<br>
                or use voice input to get started.
            </div>
            <div class="hero-badges">
                <span class="hero-badge">🤖 {current_model}</span>
                <span class="hero-badge">💬 {current_mode}</span>
                <span class="hero-badge">⚡ Streaming</span>
                <span class="hero-badge">🖼️ Vision</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Stunning suggestion cards
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Card 1: Explain a concept - with difficulty toggle
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">💡</span>
                <div class="suggestion-title">Explain a concept</div>
                <div class="suggestion-desc">Random tech concept with explanations & interview Q</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Difficulty toggle
        diff_col1, diff_col2 = st.columns([2, 3])
        with diff_col1:
            st.selectbox(
                "Difficulty",
                options=["Beginner", "Intermediate", "Advanced"],
                key="concept_difficulty",
                label_visibility="collapsed"
            )
        with diff_col2:
            st.button(
                "💡 Random Concept",
                use_container_width=True,
                key="sug1",
                on_click=trigger_concept_explainer,
            )
        
        # Card 3: Debug my code - Random bug generator
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">🔧</span>
                <div class="suggestion-title">Debug Practice</div>
                <div class="suggestion-desc">Random buggy code snippet to find and fix</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "🔧 Random Bug Challenge",
            use_container_width=True,
            key="sug3",
            on_click=trigger_bug_debugger,
        )
            
    with col2:
        # Card 2: Write something - with tone control
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">✍️</span>
                <div class="suggestion-title">Write something</div>
                <div class="suggestion-desc">Random writing task: emails, docs, creative content</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Tone toggle
        tone_col1, tone_col2 = st.columns([2, 3])
        with tone_col1:
            st.selectbox(
                "Tone",
                options=["Formal", "Friendly", "Humorous"],
                key="writing_tone",
                label_visibility="collapsed"
            )
        with tone_col2:
            st.button(
                "✍️ Random Writing",
                use_container_width=True,
                key="sug2",
                on_click=trigger_writing_generator,
            )
        
        # Card 4: Image Analysis (unchanged)
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">🖼️</span>
                <div class="suggestion-title">Analyze an image</div>
                <div class="suggestion-desc">Upload and get insights from images</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "🖼️ Analyze an image",
            use_container_width=True,
            key="sug4",
            on_click=set_empty_state_action,
            args=("",),
            kwargs={"show_image_upload": True},
        )
    
    # Show feature panels based on selection
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Concept Explainer Panel
    if st.session_state.get("show_concept_explainer") and st.session_state.get("current_concept"):
        concept = st.session_state.current_concept
        difficulty = st.session_state.get("concept_difficulty", "Intermediate")
        
        with st.container():
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%); 
                            border: 1px solid #10a37f; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
                    <h3 style="color: #10a37f; margin-bottom: 0.5rem;">💡 Random Concept Challenge</h3>
                    <p style="color: #8e8e8e; font-size: 0.9rem;">Difficulty: <strong style="color: #ececec;">{difficulty}</strong></p>
                    <div style="background: #2f2f2f; border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                        <span style="color: #10a37f; font-size: 0.8rem;">{concept['category']}</span>
                        <h4 style="color: #fff; margin: 0.5rem 0;">{concept['topic']}</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns([2, 2, 1])
            with col_a:
                if st.button("🚀 Explain This!", key="send_concept", use_container_width=True):
                    prompt = generate_concept_prompt(concept, difficulty)
                    st.session_state.pending_prompt = prompt
                    st.session_state.auto_send_prompt = True
                    st.session_state.show_concept_explainer = False
                    st.rerun()
            with col_b:
                if st.button("🎲 New Concept", key="new_concept", use_container_width=True):
                    trigger_concept_explainer()
                    st.rerun()
            with col_c:
                if st.button("✕", key="close_concept"):
                    st.session_state.show_concept_explainer = False
                    st.rerun()
    
    # Writing Generator Panel
    if st.session_state.get("show_writing_generator") and st.session_state.get("current_writing_task"):
        task = st.session_state.current_writing_task
        tone = st.session_state.get("writing_tone", "Formal")
        
        with st.container():
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%); 
                            border: 1px solid #f59e0b; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
                    <h3 style="color: #f59e0b; margin-bottom: 0.5rem;">✍️ Random Writing Task</h3>
                    <p style="color: #8e8e8e; font-size: 0.9rem;">Tone: <strong style="color: #ececec;">{tone}</strong></p>
                    <div style="background: #2f2f2f; border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                        <span style="color: #f59e0b; font-size: 0.8rem;">{task['type']}</span>
                        <h4 style="color: #fff; margin: 0.5rem 0; font-size: 1rem;">{task['prompt']}</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns([2, 2, 1])
            with col_a:
                if st.button("🚀 Generate This!", key="send_writing", use_container_width=True):
                    prompt = generate_writing_prompt(task, tone)
                    st.session_state.pending_prompt = prompt
                    st.session_state.auto_send_prompt = True
                    st.session_state.show_writing_generator = False
                    st.rerun()
            with col_b:
                if st.button("🎲 New Task", key="new_writing", use_container_width=True):
                    trigger_writing_generator()
                    st.rerun()
            with col_c:
                if st.button("✕", key="close_writing"):
                    st.session_state.show_writing_generator = False
                    st.rerun()
    
    # Bug Debugger Panel
    if st.session_state.get("show_bug_debugger") and st.session_state.get("current_bug"):
        bug = st.session_state.current_bug
        
        with st.container():
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%); 
                            border: 1px solid #ef4444; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
                    <h3 style="color: #ef4444; margin-bottom: 0.5rem;">🔧 Debug Challenge</h3>
                    <p style="color: #8e8e8e; font-size: 0.9rem;">Language: <strong style="color: #ececec;">{bug['language'].upper()}</strong></p>
                    <div style="background: #2f2f2f; border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                        <span style="color: #ef4444; font-size: 0.8rem;">🐛 Bug Type</span>
                        <h4 style="color: #fff; margin: 0.5rem 0;">{bug['title']}</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Show buggy code
            st.markdown("**🔍 Find the bug in this code:**")
            st.code(bug['buggy_code'], language=bug['language'])
            
            col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
            with col_a:
                if st.button("🚀 Analyze Bug!", key="send_bug", use_container_width=True):
                    prompt = generate_bug_prompt(bug)
                    st.session_state.pending_prompt = prompt
                    st.session_state.auto_send_prompt = True
                    st.session_state.show_bug_debugger = False
                    st.rerun()
            with col_b:
                if st.button("👀 Show Answer", key="show_answer", use_container_width=True):
                    st.session_state[f"show_bug_answer_{id(bug)}"] = True
            with col_c:
                if st.button("🎲 New Bug", key="new_bug", use_container_width=True):
                    trigger_bug_debugger()
                    st.rerun()
            with col_d:
                if st.button("✕", key="close_bug"):
                    st.session_state.show_bug_debugger = False
                    st.rerun()
            
            # Show answer if requested
            if st.session_state.get(f"show_bug_answer_{id(bug)}"):
                st.markdown("---")
                st.markdown("**✅ Fixed Code:**")
                st.code(bug['fixed_code'], language=bug['language'])
                st.markdown(f"**💡 Explanation:** {bug['explanation']}")
                st.markdown(f"**🛡️ Prevention:** {bug['prevention']}")
