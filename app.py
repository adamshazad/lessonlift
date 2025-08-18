import streamlit as st
from fpdf import FPDF
import io
import textwrap
import base64
import re

# --- Page config ---
st.set_page_config(page_title="LessonLift", page_icon="📚", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 8px;
        padding: 8px 24px;
        margin-top: 10px;
    }
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        border-radius: 6px;
        padding: 6px;
        border: 1px solid #ccc;
    }
    h1 {
        color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# --- Logo ---
st.image("logo.png", width=150)

# --- Title ---
st.markdown("<h1>📚 LessonLift - AI Lesson Planner</h1>", unsafe_allow_html=True)
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Lesson inputs ---
year_group = st.selectbox("Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
subject = st.text_input("Subject", "")
topic = st.text_input("Topic", "")
learning_objective = st.text_area("Learning Objective (optional)", "")
ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
lesson_duration = st.text_input("Lesson Duration (minutes)", "")
sen_notes = st.text_area("SEN/EAL Notes (optional)", "")

def clean_filename(text):
    """Remove spaces/special characters for safe filenames."""
    return re.sub(r'[^A-Za-z0-9_-]', '_', text.replace(" ", "_"))

if st.button("Generate Lesson Plan"):
    # --- Create lesson plan text ---
    lesson_plan = f"""
{year_group} {subject} Lesson Plan: {topic}

Learning Objective: {learning_objective if learning_objective else 'N/A'}
Ability Level: {ability_level}
Duration: {lesson_duration} minutes
SEN/EAL Notes: {sen_notes if sen_notes else 'None'}

Lesson Stages:
1. Introduction: Starter activity and objectives.
2. Teaching & Modelling: Introduce and demonstrate topic.
3. Guided Practice: Activities to reinforce learning.
4. Independent Practice: Students work individually or in groups.
5. Plenary: Review and assess understanding.

Differentiation: Adapt activities for different abilities.
Assessment: Observe and record progress.
"""

    # --- Display in textarea ---
    st.text_area("Generated Lesson Plan", lesson_plan, height=400)

    # --- Create PDF ---
    pdf_buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # PDF title
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, f"{year_group} {subject} Lesson Plan: {topic}")
    pdf.ln(5)

    # PDF content
    pdf.set_font("Arial", "", 12)
    max_chars = 90
    for paragraph in lesson_plan.split("\n\n"):
        for line in paragraph.split("\n"):
            wrapped_lines = textwrap.wrap(line.strip(), width=max_chars)
            for wl in wrapped_lines:
                pdf.multi_cell(0, 8, wl)
        pdf.ln(3)

    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    # --- Display PDF preview in browser ---
    b64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    pdf_buffer.seek(0)

    # --- Safe download button ---
    safe_filename = f"{clean_filename(year_group)}_{clean_filename(subject)}_{clean_filename(topic)}.pdf"
    st.download_button(
        label="📥 Download Lesson Plan as PDF",
        data=pdf_buffer,
        file_name=safe_filename,
        mime="application/pdf"
    )
