# -------------------------------
# App.py - LessonLift (Locked Format Version)
# -------------------------------

import os
import streamlit as st
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
import datetime
import openai

# ----------------------------------
# Streamlit Config
# ----------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# ----------------------------------
# CSS - Professional Clean Format
# ----------------------------------
st.markdown("""
<style>
.stCard {
    background-color: #f9f9f9 !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 18px !important;
    margin-bottom: 16px !important;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.12) !important;
    white-space: pre-wrap;
    line-height: 1.55em;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Session Defaults
# ----------------------------------
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "lesson_count" not in st.session_state:
    st.session_state.lesson_count = 0
if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = datetime.date.today()

# Reset daily count at midnight
today = datetime.date.today()
if st.session_state.last_reset_date != today:
    st.session_state.lesson_count = 0
    st.session_state.last_reset_date = today

# ----------------------------------
# OpenAI API Key (From Secrets)
# ----------------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# ----------------------------------
# Clean Markdown (Fixes Spacing)
# ----------------------------------
def clean_markdown(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.replace("\r", "")                     # remove weird returns
    text = re.sub(r"\n{3,}", "\n\n", text)            # remove triple spacing
    text = re.sub(r" {2,}", " ", text)                # remove double spaces
    text = re.sub(r"\*\*", "", text)                  # bold cleanup
    text = re.sub(r"`", "", text)                     # code cleanup

    return text.strip()

# ----------------------------------
# PDF Export (NO emojis)
# ----------------------------------
def create_pdf(text):
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # strip emojis

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    clean_style = ParagraphStyle(
        'Clean',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        spaceAfter=8
    )

    story = []
    for line in text.split("\n"):
        if not line.strip():
            story.append(Spacer(1, 6))
        else:
            safe_line = line.replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_line, clean_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ----------------------------------
# DOCX Export (Emojis allowed)
# ----------------------------------
def create_docx(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# ----------------------------------
# Generate Plan
# ----------------------------------
def generate_and_display_plan(prompt, title="Lesson Plan"):
    daily_limit = 10

    if st.session_state.lesson_count >= daily_limit:
        st.error("🚫 Daily limit reached.")
        return

    st.session_state.lesson_count += 1

    with st.spinner("✨ Generating lesson plan…"):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            output = response.choices[0].message.content

            # ----------------------------------
            # Add Emojis ONLY in preview/dox/txt
            # ----------------------------------
            output = output.replace("Introduction", "✨ Introduction")
            output = output.replace("Main Activity", "🛠️ Main Activity")
            output = output.replace("Closing", "✅ Closing")
            output = output.replace("Assessment", "📝 Assessment")
            output = output.replace("Extension", "⚡ Extension Activity")
            output = output.replace("Support", "🤝 Support")

            clean_output = clean_markdown(output)

            st.session_state.lesson_history.append({"title": title, "content": clean_output})

            # ------- PREVIEW -------
            st.markdown(f"### 📖 {title}")
            st.markdown(f"<div class='stCard'>{clean_output}</div>", unsafe_allow_html=True)

            # ------- DOWNLOADS -------
            pdf_buffer = create_pdf(clean_output)
            docx_buffer = create_docx(clean_output)

            st.download_button("⬇ PDF (No Emojis)", pdf_buffer, file_name="lesson_plan.pdf")
            st.download_button("⬇ DOCX", docx_buffer, file_name="lesson_plan.docx")
            st.download_button(
                "⬇ TXT",
                clean_output,
                file_name="lesson_plan.txt"
            )

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")

# ----------------------------------
# Main UI
# ----------------------------------
def lesson_generator_page():

    st.title("📚 LessonLift - AI Lesson Planner")

    with st.form("lesson_form"):
        year = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        subject = st.text_input("Subject", placeholder="e.g. Maths, English, Science")
        topic = st.text_input("Topic", placeholder="e.g. Fractions, Shapes, Plants")
        duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
        ability = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lo = st.text_area("Learning Objective (optional)")
        sen = st.text_area("SEN/EAL Notes (optional)")

        submit = st.form_submit_button("🚀 Generate Lesson Plan")

    if submit:
        prompt = f"""
Create a UK primary school lesson plan with UK spelling.

Year Group: {year}
Subject: {subject}
Topic: {topic}
Lesson Duration: {duration}
Ability Level: {ability}
Learning Objective: {lo or "Not specified"}
SEN/EAL Notes: {sen or "None"}

Make the format clean, structured and teacher-friendly.
"""
        generate_and_display_plan(prompt, title=f"{year} {subject} Lesson Plan: {topic}")

# ----------------------------------
# Sidebar Lesson History
# ----------------------------------
def show_lesson_history():
    st.sidebar.title("📜 History")
    for entry in reversed(st.session_state.lesson_history):
        with st.sidebar.expander(entry["title"]):
            st.markdown(f"<div class='stCard'>{entry['content']}</div>", unsafe_allow_html=True)

# ----------------------------------
# RUN
# ----------------------------------
show_lesson_history()
lesson_generator_page()
