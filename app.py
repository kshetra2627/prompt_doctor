"""Prompt Doctor — Streamlit prompt engineering lab with domain-specific challenges and progress persistence."""

import os
import base64
import streamlit as st
from levels import get_domain_names, get_domain, get_level, get_principles_text, get_challenge_data
from runner import run_prompt
from examiner import grade_prompt

# Load background image as base64
bg_path = os.path.join(os.path.dirname(__file__), "bg.png")
bg_data_uri = ""
if os.path.exists(bg_path):
    with open(bg_path, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()
        bg_data_uri = f"data:image/png;base64,{bg_b64}"

# Page config
st.set_page_config(
    page_title="Prompt Doctor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS with dimmed background, light colors, glass-morphism ──
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* ── Dimmed background (darker overlay) ── */
    .stApp {
        background: linear-gradient(rgba(6, 8, 20, 0.93), rgba(6, 8, 20, 0.96)),
                    url('BG_PLACEHOLDER') no-repeat center center fixed;
        background-size: cover;
    }

    /* Ambient glow blobs */
    .stApp::before {
        content: '';
        position: fixed;
        top: -20%;
        left: -10%;
        width: 55vw;
        height: 55vw;
        background: radial-gradient(ellipse, rgba(90, 120, 220, 0.12) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }
    .stApp::after {
        content: '';
        position: fixed;
        bottom: -20%;
        right: -10%;
        width: 50vw;
        height: 50vw;
        background: radial-gradient(ellipse, rgba(160, 80, 220, 0.1) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Glass cards ── */
    .glass-card {
        background: rgba(255, 255, 255, 0.045);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.4rem;
        border: 1px solid rgba(255, 255, 255, 0.07);
        box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
        transition: border-color 0.3s, box-shadow 0.3s;
        position: relative;
        z-index: 1;
    }
    .glass-card:hover {
        border-color: rgba(122, 169, 255, 0.2);
        box-shadow: 0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(122,169,255,0.08), inset 0 1px 0 rgba(255,255,255,0.08);
    }

    /* ── Title ── */
    .main-title {
        background: linear-gradient(135deg, #7aa9ff 0%, #a0d8ff 45%, #c8b8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px;
        line-height: 1;
        filter: drop-shadow(0 0 32px rgba(122, 169, 255, 0.25));
    }
    .main-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.45);
        font-size: 1rem;
        margin-bottom: 1.6rem;
        font-weight: 400;
        letter-spacing: 0.4px;
    }

    /* ── Text ── */
    .stMarkdown, .stText, label, .stSelectbox label, .stTextArea label {
        color: rgba(255, 255, 255, 0.88) !important;
    }

    /* ── Card header ── */
    .card-header {
        font-weight: 700;
        font-size: 1.35rem !important;
        margin-bottom: 1rem;
        color: #e8eeff !important;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Level badges ── */
    .level-badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.88rem !important;
        text-align: center;
        min-width: 54px;
        letter-spacing: 0.3px;
    }
    .level-active {
        background: linear-gradient(135deg, #6b9fff, #3a6dbf);
        color: white;
        box-shadow: 0 0 16px rgba(107,159,255,0.45), 0 2px 8px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.15);
    }
    .level-cleared {
        background: linear-gradient(135deg, #2edb72, #0e8a62);
        color: white;
        box-shadow: 0 0 14px rgba(46,219,114,0.35);
    }
    .level-locked {
        background: rgba(255,255,255,0.05);
        color: rgba(255,255,255,0.3);
        border: 1px solid rgba(255,255,255,0.04);
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: border-color 0.2s !important;
    }
    .stSelectbox > div > div:hover { border-color: #6b9fff !important; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: transform 0.2s, box-shadow 0.2s, background 0.2s !important;
        font-size: 0.95rem !important;
        padding: 0.55rem 1.1rem !important;
        letter-spacing: 0.2px !important;
    }
    .stButton > button:hover { transform: translateY(-2px); }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6b9fff, #3a6dbf) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        box-shadow: 0 4px 16px rgba(107,159,255,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #80adff, #4a7dcf) !important;
        box-shadow: 0 6px 24px rgba(107,159,255,0.45) !important;
    }
    .stButton > button:not([kind]) {
        background: rgba(255,255,255,0.06) !important;
        color: rgba(255,255,255,0.85) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
    }
    .stButton > button:not([kind]):hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.18) !important;
    }

    /* ── Textarea ── */
    .stTextArea textarea {
        border-radius: 12px !important;
        background: rgba(0,0,0,0.6) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        font-size: 0.97rem !important;
        color: #ffffff !important;
        caret-color: #7aa9ff !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus {
        border-color: #6b9fff !important;
        box-shadow: 0 0 0 3px rgba(107,159,255,0.18) !important;
        background: rgba(0,0,0,0.7) !important;
    }
    .stTextArea textarea::placeholder { color: rgba(255,255,255,0.3) !important; }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: rgba(255,255,255,0.88) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        transition: background 0.2s !important;
    }
    .streamlit-expanderHeader:hover { background: rgba(255,255,255,0.07) !important; }
    .streamlit-expanderContent {
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem !important;
        background: rgba(255,255,255,0.02) !important;
    }

    /* ── Verdict panels ── */
    .verdict-pass {
        background: linear-gradient(135deg, #2edb72, #0e8a62);
        color: white; padding: 1.1rem; border-radius: 14px;
        text-align: center; font-weight: 700; font-size: 1.35rem !important;
        box-shadow: 0 6px 28px rgba(46,219,114,0.35), inset 0 1px 0 rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .verdict-revise {
        background: linear-gradient(135deg, #e84460, #d040b0);
        color: white; padding: 1.1rem; border-radius: 14px;
        text-align: center; font-weight: 700; font-size: 1.35rem !important;
        box-shadow: 0 6px 28px rgba(232,68,96,0.35), inset 0 1px 0 rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .verdict-error {
        background: linear-gradient(135deg, #3a9ffd, #00ccff);
        color: white; padding: 1.1rem; border-radius: 14px;
        text-align: center; font-weight: 700; font-size: 1.35rem !important;
        box-shadow: 0 6px 28px rgba(58,159,253,0.35), inset 0 1px 0 rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* ── Principle items ── */
    .principle-pass {
        background: rgba(46, 219, 114, 0.08);
        border-left: 3px solid #2edb72;
        padding: 0.75rem 1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.5rem;
        color: rgba(255,255,255,0.88);
    }
    .principle-fail {
        background: rgba(232, 68, 96, 0.08);
        border-left: 3px solid #e84460;
        padding: 0.75rem 1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.5rem;
        color: rgba(255,255,255,0.88);
    }

    /* ── Level progress bar ── */
    .level-progress-container { display: flex; gap: 0.5rem; margin: 0.8rem 0; }
    .level-dot {
        flex: 1; height: 6px; border-radius: 3px;
        transition: background 0.3s, box-shadow 0.3s;
        min-width: 28px;
    }

    /* ── Alerts ── */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        background: rgba(255,255,255,0.04) !important;
        color: rgba(255,255,255,0.88) !important;
    }
    .stAlert > div { color: rgba(255,255,255,0.88) !important; }

    /* ── Divider ── */
    hr {
        margin: 1.4rem 0 !important;
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(107,159,255,0.25), transparent) !important;
    }

    /* ── Code blocks ── */
    .stCode {
        border-radius: 10px !important;
        background: rgba(0,0,0,0.45) !important;
        color: rgba(255,255,255,0.92) !important;
    }

    /* ── Domain badge ── */
    .domain-badge {
        padding: 0.75rem 1.1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }

    /* ── Progress info ── */
    .progress-info {
        font-size: 0.95rem;
        font-weight: 500;
        color: rgba(255,255,255,0.55);
        padding: 0.4rem 0;
        letter-spacing: 0.3px;
    }

    /* ── Level header ── */
    .level-header {
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .level-header .level-desc { opacity: 0.92; margin-top: 0.3rem; font-size: 1.05rem; }
</style>
"""
st.markdown(CSS.replace("BG_PLACEHOLDER", bg_data_uri) if bg_data_uri else CSS, unsafe_allow_html=True)

# ── Session state with persistence ──────────────────────────────────────
for key, default in [
    ("level", 1),
    ("domain", None),
    ("challenge", 1),
    ("verdict", None),
    ("model_output", ""),
    ("submitted", False),
    ("cleared_levels", set()),
    ("completed_challenges", set()),
    ("user_progress", {}),  # {domain: {challenge_id: completed_level}}
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Title with bandaid fix (light colored) ──────────────────────────────
st.markdown(
    '<div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 0;">'
    '<span style="font-size: 42px; color: #80d4ff; filter: drop-shadow(0 0 20px rgba(128, 212, 255, 0.3));">🩺</span>'
    '<div class="main-title">Prompt Doctor</div>'
    '</div>',
    unsafe_allow_html=True
)
st.markdown('<div class="main-subtitle">Write a prompt. Get graded by an AI examiner. Level up through 5 techniques.</div>', unsafe_allow_html=True)

# ── Single column layout (removed side-by-side) ─────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="card-header">📋 Your Prompt Lab</div>', unsafe_allow_html=True)

# Domain dropdown selector
domain_names = get_domain_names()
selected_domain = st.selectbox(
    "Choose your domain",
    [""] + domain_names,
    format_func=lambda x: "Select a domain..." if x == "" else f"{x} — {get_domain(x)['description']}" if x else "",
    key="domain_selector",
)

if selected_domain:
    # Check if domain changed - load saved progress
    if st.session_state.domain != selected_domain:
        st.session_state.domain = selected_domain
        # Load saved progress for this domain
        progress = st.session_state.user_progress.get(selected_domain, {})
        # Find the first incomplete challenge
        for ch in range(1, 6):
            if ch not in progress or progress.get(ch, 0) < 5:
                st.session_state.challenge = ch
                st.session_state.level = progress.get(ch, 1)
                break
        else:
            st.session_state.challenge = 5
            st.session_state.level = 5
        st.session_state.verdict = None
        st.session_state.model_output = ""
        st.session_state.submitted = False
        st.session_state.cleared_levels = set()
        st.rerun()

    domain_data = get_domain(selected_domain)
    challenge_num = st.session_state.challenge
    level = st.session_state.level

    # Get challenge data
    challenge_data = get_challenge_data(selected_domain, challenge_num)

    if not challenge_data:
        st.error(f"Challenge {challenge_num} not found for {selected_domain}")
    else:
        # ── Domain badge with gradient ──
        domain_colors = {
            "Healthcare": ("#ff6b6b", "#ee5a24"),
            "Legal": ("#7aa9ff", "#4a7dcf"),
            "Finance": ("#4facfe", "#00f2fe"),
            "Technology": ("#c8b8ff", "#7aa9ff"),
            "Education": ("#f093fb", "#f5576c"),
            "Marketing": ("#ffd93d", "#f5576c"),
            "Environmental": ("#38ef7d", "#11998e"),
            "HR": ("#4facfe", "#764ba2"),
        }
        dc = domain_colors.get(selected_domain, ("#7aa9ff", "#4a7dcf"))
        st.markdown(
            f'<div class="domain-badge" style="background: linear-gradient(135deg, {dc[0]}, {dc[1]});">'
            f'<strong>{selected_domain}</strong> &mdash; {domain_data["base_scenario"]}'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Change Domain button (False removed) ──
        if st.button("🔄 Change Domain", use_container_width=True):
            st.session_state.domain = None
            st.session_state.challenge = 1
            st.session_state.level = 1
            st.session_state.verdict = None
            st.session_state.model_output = ""
            st.session_state.submitted = False
            st.session_state.cleared_levels = set()
            st.rerun()

        # ── Progress Info ──
        completed = len([c for c in range(1, 6) if c in st.session_state.completed_challenges])
        st.markdown(
            f'<div class="progress-info">'
            f'📊 Challenge {challenge_num}/5 • Level {level}/5 • '
            f'Completed: {completed}/5 challenges'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Level progress bar ──
        st.markdown("### Level Progress")
        progress_html = '<div class="level-progress-container">'
        for i in range(1, 6):
            if i in st.session_state.cleared_levels:
                progress_html += f'<div class="level-dot" style="background: linear-gradient(135deg, #38ef7d, #11998e);"></div>'
            elif i == level:
                progress_html += f'<div class="level-dot" style="background: linear-gradient(135deg, #7aa9ff, #4a7dcf);"></div>'
            else:
                progress_html += f'<div class="level-dot" style="background: rgba(255,255,255,0.1);"></div>'
        progress_html += '</div>'
        st.markdown(progress_html, unsafe_allow_html=True)

        # ── Level badges ──
        level_cols = st.columns(5)
        level_names = {1: "Basic", 2: "Structured", 3: "Few-shot", 4: "Reasoning", 5: "Robust"}
        for i in range(1, 6):
            with level_cols[i - 1]:
                if i in st.session_state.cleared_levels:
                    st.markdown(f'<div class="level-badge level-cleared">✅ L{i}</div>', unsafe_allow_html=True)
                elif i == level:
                    st.markdown(f'<div class="level-badge level-active">L{i}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="level-badge level-locked">L{i}</div>', unsafe_allow_html=True)
                st.caption(level_names[i])

        # ── Level data ──
        level_data = get_level(selected_domain, level, challenge_num)

        if level_data:
            st.markdown("---")
            
            # ── Level header ──
            level_gradients = {
                1: "linear-gradient(135deg, #7aa9ff, #4a7dcf)",
                2: "linear-gradient(135deg, #f093fb, #f5576c)",
                3: "linear-gradient(135deg, #4facfe, #00f2fe)",
                4: "linear-gradient(135deg, #38ef7d, #11998e)",
                5: "linear-gradient(135deg, #ffd93d, #f5576c)",
            }
            lg = level_gradients.get(level, "linear-gradient(135deg, #7aa9ff, #4a7dcf)")

            # Show ONLY context (role is implicit)
            st.markdown(
                f'<div class="level-header" style="background: {lg};">'
                f'<div class="level-desc" style="font-size: 1.2rem;">📝 {challenge_data["context"]}</div>'
                f'<div style="margin-top: 0.5rem; opacity: 0.8; font-size: 0.95rem;">💡 Hint: What role would you need to play to handle this scenario?</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Task description
            st.markdown(f"**Level {level}: {level_data['name']}**")
            st.markdown(level_data["description"])
            st.markdown(f"**Task:** {level_data['task']}")

            # ── Sample Input ──
            with st.expander("📄 Sample Input", expanded=True):
                st.code(level_data["sample_input"], language="text")

            # ── Expected Output ──
            with st.expander("🎯 Expected Output", expanded=True):
                st.info(level_data.get("output_expectation", "No specific output expectation defined."))

            # ── Example Output ──
            with st.expander("📝 Example Output", expanded=True):
                example = level_data.get("example_output", "")
                if example:
                    st.code(example, language="text")
                else:
                    st.info("No example output defined for this level.")

            # ── Principles ──
            with st.expander("📋 What the Examiner Checks", expanded=True):
                st.markdown(get_principles_text(selected_domain, level, challenge_num))

            # ── Prompt Editor ──
            st.markdown("### ✏️ Your Prompt")
            domain_lower = selected_domain.lower()
            prompt = st.text_area(
                "Write your prompt below. It will be run against the sample input.",
                height=250,
                placeholder=(
                    f"You are a {domain_lower} expert...\n\n"
                    f"Analyze the following input and..."
                ),
                key=f"prompt_{selected_domain}_{challenge_num}_{level}", 
            )

            # ── Submit and Reset ──
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.button("🚀 Submit Prompt", type="primary", use_container_width=True)
            with col2:
                if st.button("🔄 Reset Level", use_container_width=True):
                    st.session_state.verdict = None
                    st.session_state.model_output = ""
                    st.session_state.submitted = False
                    st.rerun()

            # ── Run the prompt ──
            if submitted and prompt.strip():
                with st.spinner("Running your prompt against the sample input..."):
                    st.session_state.submitted = True
                    model_output = run_prompt(prompt.strip(), level_data["sample_input"])
                    st.session_state.model_output = model_output

                if model_output.startswith("ERROR"):
                    st.error(model_output)
                else:
                    with st.spinner("The Examiner is grading your prompt..."):
                        principles_text = get_principles_text(selected_domain, level, challenge_num)
                        verdict = grade_prompt(
                            domain_name=selected_domain,
                            level_num=level,
                            level_name=level_data["name"],
                            principles_text=principles_text,
                            output_expectation=level_data.get("output_expectation", ""),
                            example_output=level_data.get("example_output", ""),
                            student_prompt=prompt.strip(),
                            sample_input=level_data["sample_input"],
                            model_output=model_output,
                        )
                        st.session_state.verdict = verdict
                        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── Verdict Panel ──────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="card-header">🔍 Examiner Verdict</div>', unsafe_allow_html=True)

if not st.session_state.submitted:
    st.info(
        "💡 **Ready to start?** Select a domain above, write a prompt, "
        "and submit it. The Examiner will grade it against this level's principles."
    )
    st.markdown(
        '<div style="text-align: center; padding: 3rem 1rem; color: rgba(255,255,255,0.3); font-size: 3rem;">'
        '🎯<br>'
        '<div style="font-size: 1.1rem; margin-top: 0.5rem;">Your verdict will appear here</div>'
        '</div>',
        unsafe_allow_html=True
    )

elif st.session_state.verdict:
    verdict = st.session_state.verdict

    # ── Verdict banner ──
    if verdict.get("verdict") == "pass":
        st.markdown(
            '<div class="verdict-pass">✅ PASS — All principles satisfied!</div>',
            unsafe_allow_html=True
        )
    elif verdict.get("verdict") == "error":
        st.markdown(
            '<div class="verdict-error">⚠️ ERROR — Something went wrong during grading.</div>',
            unsafe_allow_html=True
        )
        if verdict.get("raw_response"):
            with st.expander("📄 Raw Judge Response", expanded=True):
                st.code(verdict["raw_response"], language="text")
    else:
        st.markdown(
            '<div class="verdict-revise">📝 REVISE — Some principles need work.</div>',
            unsafe_allow_html=True
        )

    # ── Per-principle check ──
    st.markdown("### Per-Principle Check")
    principles = verdict.get("principles", [])
    for p in principles:
        passed = p.get("pass", False)
        name = p.get("name", "unknown")
        weakness = p.get("weakness", "")
        question = p.get("question", "")

        if passed:
            st.markdown(
                f'<div class="principle-pass">'
                f'✅ <strong>{p.get("label", name)}</strong> — Pass'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            fail_html = (
                f'<div class="principle-fail">'
                f'❌ <strong>{p.get("label", name)}</strong> — Fail'
            )
            if weakness:
                fail_html += f'<br><span style="color: #f87171; font-size: 0.95rem;">🎯 Weakness: {weakness}</span>'
            if question:
                fail_html += f'<br><span style="color: #93bbfc; font-size: 0.95rem;">❓ Question: {question}</span>'
            fail_html += '</div>'
            st.markdown(fail_html, unsafe_allow_html=True)

    # ── Model Output ──
    with st.expander("📤 Live Model Output", expanded=True):
        # Use st.code for better visibility (dark background)
        st.code(st.session_state.model_output, language="text")

    # ── Advance / Next Challenge ──
    if verdict.get("verdict") == "pass":
        st.markdown(
            '<div style="background: linear-gradient(135deg, #38ef7d, #11998e); color: white; '
            'padding: 1.2rem; border-radius: 16px; text-align: center; font-weight: 700; font-size: 1.2rem; '
            'margin: 1rem 0; border: 1px solid rgba(255,255,255,0.1);">'
            '🎉 You passed this level!</div>',
            unsafe_allow_html=True
        )
        
        # Mark this level as cleared
        st.session_state.cleared_levels.add(level)
        
        # Save progress
        if selected_domain not in st.session_state.user_progress:
            st.session_state.user_progress[selected_domain] = {}
        st.session_state.user_progress[selected_domain][challenge_num] = level
        
        # Check if all levels cleared for this challenge
        if len(st.session_state.cleared_levels) >= 5:
            st.session_state.completed_challenges.add(challenge_num)
            
            # Check if all challenges completed
            if len(st.session_state.completed_challenges) >= 5:
                st.balloons()
                st.markdown(
                    '<div style="background: linear-gradient(135deg, #ffd93d, #f5576c); color: white; '
                    'padding: 2rem; border-radius: 20px; text-align: center; margin: 1rem 0; '
                    'border: 1px solid rgba(255,255,255,0.1);">'
                    '<div style="font-size: 2.5rem; font-weight: 800;">🏆 Congratulations!</div>'
                    f'<div style="margin-top: 0.8rem; font-size: 1.3rem;">You\'ve completed all 5 challenges in '
                    f'<strong>{st.session_state.domain}</strong>!</div>'
                    '<div style="margin-top: 0.8rem; opacity: 0.9;">You\'ve built prompts using: role & instruction, '
                    'structured output, few-shot learning, chain-of-thought reasoning, and defensive constraints.</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                # Show next challenge button
                if st.button("➡️ Next Challenge", type="primary", use_container_width=True):
                    st.session_state.challenge = challenge_num + 1
                    st.session_state.level = 1
                    st.session_state.cleared_levels = set()
                    st.session_state.verdict = None
                    st.session_state.model_output = ""
                    st.session_state.submitted = False
                    st.rerun()
        else:
            # Show next level button
            if st.button("➡️ Next Level", type="primary", use_container_width=True):
                st.session_state.level = level + 1
                st.session_state.verdict = None
                st.session_state.model_output = ""
                st.session_state.submitted = False
                st.rerun()

elif st.session_state.submitted and st.session_state.model_output:
    st.info("⏳ Waiting for the Examiner's verdict...")
    st.markdown("### Model Output So Far")
    st.code(st.session_state.model_output, language="text")
    st.caption("The verdict should appear momentarily. If not, try submitting again.")

else:
    st.info("Submit a prompt to see the verdict.")

if st.session_state.verdict:
    with st.expander("⚙️ Raw Verdict JSON", expanded=False):
        st.json(st.session_state.verdict)

st.markdown('</div>', unsafe_allow_html=True)