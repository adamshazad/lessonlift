# app.py
import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# -------------------------------
# CSS
# -------------------------------
st.markdown("""
<style>
body {background-color: white; color: black;}
.stTextInput>div>div>input, textarea, select {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ccc !important;
    padding: 8px !important;
    border-radius: 5px !important;
}
.stCard {
    background-color: #f9f9f9 !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.5em;
    max-height: 300px;
    overflow-y: auto;
}
/* --- Sidebar Fix --- */
[data-testid="stSidebar"][aria-expanded="false"] {
    display: none !important;
}
[data-testid="stSidebar"] {
    max-width: 250px !important;
    min-width: 0px !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Session defaults
# -------------------------------
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "lesson_count" not in st.session_state:
    st.session_state.lesson_count = 0
if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = datetime.date.today()
if "lesson_cache" not in st.session_state:
    st.session_state.lesson_cache = {}
if "trial_start_date" not in st.session_state:
    st.session_state.trial_start_date = datetime.date.today()
    st.session_state.trial = True

# Reset daily count at midnight
today = datetime.date.today()
if st.session_state.last_reset_date != today:
    st.session_state.lesson_count = 0
    st.session_state.last_reset_date = today

# -------------------------------
# Helper: compute daily limit (trial or paid)
# -------------------------------
def get_daily_limit():
    today_local = datetime.date.today()
    if st.session_state.get("trial", False):
        days_since = (today_local - st.session_state.get("trial_start_date", today_local)).days
        if days_since >= 7:
            st.session_state.trial = False
            return 10
        else:
            return 5
    return 10

# -------------------------------
# API key(s) setup & model selection
# -------------------------------
# Read keys from secrets (preferred) or from sidebar input
api_keys = st.secrets.get("gemini_api_keys", None)
if api_keys is None:
    single_key = st.secrets.get("gemini_api", None)
    if single_key:
        api_keys = [single_key]

# Sidebar input if no secrets
if not api_keys:
    st.sidebar.title("🔑 API Key Setup")
    key_input = st.sidebar.text_input("Gemini API Key (single or comma-separated)", type="password")
    if key_input:
        # allow comma-separated keys in the sidebar
        api_keys = [k.strip() for k in key_input.split(",") if k.strip()]

if not api_keys:
    api_keys = []  # empty list if nothing provided

current_key_index = 0
model = None

# Candidate model names to try (order matters - prefer newer models first)
CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-turbo",
    "gemini-1.5-flash",
    "gemini-1.5-turbo",
    "gemini-1.5"
]

def try_setup_model():
    """
    Try to configure genai with each API key and test candidate models.
    Returns a working model object or None.
    """
    global current_key_index, model
    if not api_keys:
        return None
    tries_keys = 0
    # attempt each key, and for each, try the candidate models
    while tries_keys < len(api_keys):
        api_key = api_keys[current_key_index]
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            logger.exception("Failed to configure genai with key index %s", current_key_index)
            # rotate to next key
            current_key_index = (current_key_index + 1) % len(api_keys)
            tries_keys += 1
            continue

        # For this configured key, try candidate models
        for candidate in CANDIDATE_MODELS:
            try:
                m = genai.GenerativeModel(candidate)
                # quick lightweight test: short prompt — may still use quota but keeps it small
                try:
                    _ = m.generate_content("Ping test")
                except Exception:
                    # if generate_content fails it's not usable for this key/model, try next candidate
                    logger.debug("Model %s not usable with this key (generate_content failed).", candidate)
                    continue
                # success
                model = m
                logger.info("Using model %s with key index %s", candidate, current_key_index)
                return model
            except Exception as e:
                # instantiation failed — try next candidate
                logger.debug("Could not instantiate model %s: %s", candidate, str(e))
                continue

        # none of the candidates worked for this key -> rotate to next key
        current_key_index = (current_key_index + 1) % len(api_keys)
        tries_keys += 1

    # all keys tried and no working model
    model = None
    return None

# Attempt model setup at startup
if api_keys:
    try_setup_model()

# -------------------------------
# UI helpers
# -------------------------------
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:16px;">
                <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
                    <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;" />
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png' to the app folder.")

def title_and_tagline():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', md_text)
    text = re.sub(r'\*(.*?)\*', r'\1', md_text)
    return text

# -------------------------------
# Exporters
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    story = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            story.append(Spacer(1,6))
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, normal))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for raw in text.splitlines():
        doc.add_paragraph(raw.rstrip())
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# -------------------------------
# Generator with caching, rotation & safe errors
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    global current_key_index, model

    daily_limit = get_daily_limit()

    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached. You can generate up to {daily_limit} lessons per day.")
        return

    if not api_keys:
        st.error("⚠️ No Gemini API key found. Add it in the sidebar or in st.secrets['gemini_api'] / ['gemini_api_keys'].")
        return

    # Re-check model and try to set one up if currently not set
    if model is None:
        try_setup_model()
    if model is None:
        st.error("⚠️ Could not connect to a working model. Please check API keys and try again later.")
        return

    # Use a deterministic cache key for the prompt
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()

    # If cached, return cached content (do NOT consume daily count)
    if prompt_hash in st.session_state.lesson_cache:
        clean_output = st.session_state.lesson_cache[prompt_hash]
        # Show without using API calls or incrementing count
        st.markdown(f"### 📖 {title}")
        # Create export buffers (so downloads are available even for cached)
        pdf_buffer = create_pdf(clean_output)
        docx_buffer = create_docx(clean_output)

        # Preview box
        st.markdown("""
        <div style="
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 16px;
            background-color: #fdfdfd;
            box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
            margin-bottom: 14px;
            max-height: 400px;
            overflow-y: auto;
        ">
        """, unsafe_allow_html=True)
        st.markdown(f"{clean_output.replace(chr(10), '<br>')}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Download box
        pdf_b64 = base64.b64encode(pdf_buffer.read()).decode()
        docx_b64 = base64.b64encode(docx_buffer.read()).decode()
        txt_b64 = base64.b64encode(clean_output.encode()).decode()

        st.markdown("""
        <div style="
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 12px;
            background-color: #fafafa;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: flex-start;
        ">
        """, unsafe_allow_html=True)

        st.markdown(
            f"""
            <a href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt">
                <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ TXT</button>
            </a>
            <a href="data:application/pdf;base64,{pdf_b64}" download="lesson_plan.pdf">
                <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ PDF</button>
            </a>
            <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{docx_b64}" download="lesson_plan.docx">
                <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ DOCX</button>
            </a>
            """,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Not cached => call the API with safe rotation and retries
    with st.spinner("✨ Creating lesson plan..."):
        success = False
        attempts = 0
        max_attempts = max(1, len(api_keys))  # try up to number of keys
        last_exception = None

        while attempts < max_attempts and not success:
            try:
                # Attempt generation with current model
                response = model.generate_content(prompt)
                output = response.text.strip()
                clean_output = strip_markdown(output)

                # Save to cache & history and increment count
                st.session_state.lesson_cache[prompt_hash] = clean_output
                st.session_state.lesson_history.append({"title": title, "content": clean_output})
                st.session_state.lesson_count += 1

                success = True
                break
            except Exception as e:
                # log the real error (server logs) for debugging
                logger.exception("API generation failed on key index %s: %s", current_key_index, str(e))
                last_exception = e
                # rotate to next key and try to re-setup model
                if api_keys:
                    current_key_index = (current_key_index + 1) % len(api_keys)
                    try_setup_model()
                attempts += 1

        if not success:
            # do NOT increment lesson_count (we increment only on success)
            # Show a friendly message to the user
            st.error("⚠️ Sorry, the lesson plan could not be generated at this time. Please try again.")
            # (full error logged to server logs via logger.exception above)
            return

    # If we reach here, we have successful content in clean_output
    if regen_message:
        st.info(f"🔄 {regen_message}")

    used = st.session_state.lesson_count
    remaining = get_daily_limit() - used
    st.info(f"📊 {used}/{get_daily_limit()} lessons used today — {remaining} remaining")

    # Show latest plan with boxed preview
    st.markdown(f"### 📖 {title}")

    # Create export buffers now
    pdf_buffer = create_pdf(clean_output)
    docx_buffer = create_docx(clean_output)

    st.markdown("""
    <div style="
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 16px;
        background-color: #fdfdfd;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
        margin-bottom: 14px;
        max-height: 400px;
        overflow-y: auto;
    ">
    """, unsafe_allow_html=True)
    st.markdown(f"{clean_output.replace(chr(10), '<br>')}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Prepare base64 blobs for downloads
    pdf_b64 = base64.b64encode(pdf_buffer.read()).decode()
    docx_b64 = base64.b64encode(docx_buffer.read()).decode()
    txt_b64 = base64.b64encode(clean_output.encode()).decode()

    # Download box
    st.markdown("""
    <div style="
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 12px;
        background-color: #fafafa;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: flex-start;
    ">
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <a href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt">
            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ TXT</button>
        </a>
        <a href="data:application/pdf;base64,{pdf_b64}" download="lesson_plan.pdf">
            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ PDF</button>
        </a>
        <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{docx_b64}" download="lesson_plan.docx">
            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ DOCX</button>
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# Main generator page (form + regen)
# -------------------------------
def lesson_generator_page():
    show_logo()
    title_and_tagline()

    if not api_keys:
        st.error("No Gemini API key found. Add it in the sidebar to generate plans.")
        return

    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"], key="year_group")
        lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"], key="ability_level")
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"], key="lesson_duration")
        lesson_data['subject'] = st.text_input("Subject", placeholder="e.g. English, Maths, Science", key="subject")
        lesson_data['topic'] = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth", key="topic")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions", key="lo")
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters", key="sen")
        submitted = st.form_submit_button("🚀 Generate Lesson Plan")

    if submitted:
        prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {lesson_data['year_group']}
Subject: {lesson_data['subject']}
Topic: {lesson_data['topic']}
Learning Objective: {lesson_data['learning_objective'] or 'Not specified'}
Ability Level: {lesson_data['ability_level']}
Lesson Duration: {lesson_data['lesson_duration']}
SEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}
"""
        st.session_state.last_prompt = prompt
        generate_and_display_plan(prompt, title="Original")

    if st.session_state.last_prompt:
        st.markdown("### 🔄 Not happy with the plan?")
        regen_style = st.selectbox(
            "Choose a regeneration style:",
            [
                "♻️ Just regenerate (different variation)",
                "🎨 More creative & engaging activities",
                "📋 More structured with timings",
                "🧩 Simplify for lower ability",
                "🚀 Challenge for higher ability"
            ],
            key="regen_style"
        )
        custom_instruction = st.text_input(
            "Or type your own custom instruction (optional)",
            placeholder="e.g. Make it more interactive with outdoor activities",
            key="custom_instruction"
        )
        if st.button("🔁 Regenerate Lesson Plan", key="regen_btn"):
            extra_instruction = ""
            regen_message = ""
            if not custom_instruction:
                if regen_style == "🎨 More creative & engaging activities":
                    extra_instruction = "Make activities more creative, interactive, and fun."
                    regen_message = "Lesson updated with more creative and engaging activities."
                elif regen_style == "📋 More structured with timings":
                    extra_instruction = "Add clear structure with timings for each section."
                    regen_message = "Lesson updated with clearer structure and timings."
                elif regen_style == "🧩 Simplify for lower ability":
                    extra_instruction = "Adapt for lower ability: simpler language, more scaffolding, step-by-step."
                    regen_message = "Lesson simplified for lower ability."
                elif regen_style == "🚀 Challenge for higher ability":
                    extra_instruction = "Adapt for higher ability: include stretch/challenge tasks and deeper thinking questions."
                    regen_message = "Lesson updated with higher ability challenge tasks."
                else:
                    regen_message = "Here’s a new updated version of your lesson plan."
            else:
                extra_instruction = custom_instruction
                regen_message = f"Lesson updated: {custom_instruction}"
            new_prompt = st.session_state.last_prompt + "\n\n" + extra_instruction
            generate_and_display_plan(new_prompt, title=f"Regenerated {len(st.session_state.lesson_history)+1}", regen_message=regen_message)

# -------------------------------
# Sidebar history
# -------------------------------
def show_lesson_history():
    st.sidebar.title("📜 Lesson History")
    if st.session_state.lesson_history:
        for i, entry in enumerate(reversed(st.session_state.lesson_history), 1):
            with st.sidebar.expander(f"{entry['title']}"):
                st.markdown(f"<div class='stCard'>{entry['content'].replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.write("No lesson history yet.")

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    show_lesson_history()
    lesson_generator_page()
