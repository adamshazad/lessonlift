# -------------------------------
# LessonLift - FULL Generator (DEPLOYMENT FIXED)
# -------------------------------

import streamlit as st

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="LessonLift - AI Lesson Planner",
    layout="centered"
)

# -------------------------------
# Imports
# -------------------------------
import os
import re
import base64
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import openai

# -------------------------------
# Session State
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []

if "lesson_count" not in st.session_state:
    st.session_state.lesson_count = 0

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None

if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = datetime.date.today()

# Daily reset
today = datetime.date.today()
if st.session_state.last_reset_date != today:
    st.session_state.lesson_count = 0
    st.session_state.last_reset_date = today

# -------------------------------
# OpenAI Key (SAFE)
# -------------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

# -------------------------------
# LOGIN PAGE
# -------------------------------
def show_login():
    st.title("🔐 LessonLift Login")
    st.write("Access the full AI lesson generator")

    if st.button("Login via Bolt"):
        st.session_state.logged_in = True
        st.experimental_rerun()

# -------------------------------
# HELPERS (UNCHANGED LOGIC)
# -------------------------------
def clean_markdown(text):
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def count_words(text):
    return len(text.split()) if text else 0

# -------------------------------
# EXPORTERS (UNCHANGED)
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        'NormalFixed',
        parent=styles['Normal'],
        fontSize=11,
        leading=14
    )
    story = []
    for line in text.splitlines():
        if line.strip():
            story.append(Paragraph(line, normal))
        else:
            story.append(Spacer(1, 6))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# -------------------------------
# GENERATOR (FULL)
# -------------------------------
def generate_and_display_plan(prompt, lesson_data):
    if openai.api_key is None:
        st.error("❌ OpenAI API key missing. Generator disabled.")
        return

    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error("🚫 Daily limit reached")
        return

    st.session_state.lesson_count += 1
    st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used today")

    with st.spinner("✨ Creating lesson plan..."):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.25,
            max_tokens=2200,
        )

    raw = response.choices[0].message.content
    final = clean_markdown(raw)

    st.markdown(final)

    pdf = create_pdf(final)
    docx = create_docx(final)

    st.download_button("⬇ PDF", pdf, "lesson.pdf")
    st.download_button("⬇ DOCX", docx, "lesson.docx")

    st.session_state.lesson_history.append(final)

# -------------------------------
# MAIN GENERATOR PAGE
# -------------------------------
def generator_page():
    st.title("📚 LessonLift Generator")

    with st.form("lesson_form"):
        subject = st.text_input("Subject")
        topic = st.text_input("Topic")
        year = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        submitted = st.form_submit_button("🚀 Generate")

    if submitted:
        prompt = f"""
UK Primary Lesson Plan
Year Group: {year}
Subject: {subject}
Topic: {topic}
"""
        generate_and_display_plan(prompt, {})

# -------------------------------
# ROUTING (NO LOOPS)
# -------------------------------
if not st.session_state.logged_in:
    show_login()
else:
    generator_page()
