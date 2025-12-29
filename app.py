# -------------------------------
# App.py - LessonLift with OpenAI 1.0+ integration (fully fixed for spacing + stronger generation guard)
# -------------------------------

import os
import streamlit as st
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import datetime
import openai

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# -------------------------------
# CSS (scrollable box)
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
    padding: 12px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.45em;
    white-space: pre-wrap;
    max-height: 70vh;
    overflow-y: auto;
    font-size: 16px !important;
    font-weight: 500 !important;
}
.metadata-line {
    font-weight: bold;
    font-size: 16px !important;
    margin-top: 6px;
    margin-bottom: 6px;
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

today = datetime.date.today()
if st.session_state.last_reset_date != today:
    st.session_state.lesson_count = 0
    st.session_state.last_reset_date = today

# -------------------------------
# OpenAI key
# -------------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# -------------------------------
# CLEAN + FORMAT functions
# -------------------------------
def clean_markdown(text) -> str:
    if text is None:
        return ""
    text = str(text)
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = text.replace("•", "-")
    text = re.sub(r'^[\t\s]*[\*\u2022]\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'^[\t\s]*[-–—•]\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'\-{3,}', '', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


    def format_tight_output(text: str) -> str:
    if not text:
        return ""

    HEADER_KEYWORDS = [
        "Introduction",
        "Lesson Outline",
        "Main Activity",
        "Shape Sorting Activity",
        "Creative Shape Art",
        "Conclusion and Assessment",
        "Differentiation",
        "Assessment",
        "Resources",
        "objectives",
        "Activity"
    ]

    lines = [l.rstrip() for l in text.splitlines()]
    output = []
    last_header = None

    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue

        header_match = next((h for h in HEADER_KEYWORDS if stripped.lower().startswith(h.lower())), None)
        if header_match:
            if last_header == header_match:
                continue
            last_header = header_match

            if output and output[-1] != "":
                output.append("")  # spacing above header

            output.append(f"@@HEADER@@{header_match}@@")
            output.append("")  # spacing after header
            continue

        # Bullets with spacing
        if stripped.startswith(("-", "•", "*")) or re.match(r'^\d+[\.\)]', stripped):
            if output and output[-1] != "":
                output.append("")  # spacing above bullet
            bullet = re.sub(r'^[-•*\d\.\)]*\s*', '', stripped)
            output.append(f"- {bullet}")
            continue

        # Paragraphs
        output.append(stripped)
        output.append("")

    # Collapse multiple blank lines to one
    final = []
    for ln in output:
        if ln == "" and final and final[-1] == "":
            continue
        final.append(ln)

    return "\n".join(final).strip()


# Metadata + Preview HTML
metadata_html = f"""
<div class='stCard'>
    <div class='metadata-line'><b>Lesson Title:</b> {lesson_data.get('topic','')}</div>
    <div class='metadata-line'><b>Subject:</b> {lesson_data.get('subject','')}</div>
    <div class='metadata-line'><b>Topic:</b> {lesson_data.get('topic','')}</div>
    <div class='metadata-line'><b>Year Group:</b> {lesson_data.get('year_group','')}</div>
    <div class='metadata-line'><b>Duration:</b> {lesson_data.get('lesson_duration','')}</div>
    <div class='metadata-line'><b>Ability Level:</b> {lesson_data.get('ability_level','')}</div>
    <div class='metadata-line'><b>SEN/EAL Notes:</b> {lesson_data.get('sen_notes','None')}</div>
    <div class='metadata-line'><b>Learning Objective:</b> {lesson_data.get('learning_objective','')}</div>
    <br>
    {final_output_html.strip()}
</div>
"""
st.markdown(metadata_html, unsafe_allow_html=True)
            

            # -------------------------------
            # Exports
            pdf_buffer = create_pdf(final_output_clean)
            docx_buffer = create_docx(final_output_clean)

            st.markdown(
                f"""
<div style="display:flex; gap:10px; margin-top:16px; flex-wrap:wrap;">
    <a href="data:text/plain;base64,{base64.b64encode(final_output_clean.encode()).decode()}" download="lesson_plan.txt">
        <button style="padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ TXT</button>
    </a>
    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
        <button style="padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ PDF</button>
    </a>
    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
        <button style="padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ DOCX</button>
    </a>
</div>
""", unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")
            return

    # Save to history
    st.session_state.lesson_history.append({"title": title, "content": final_output})

    if regen_message:
        st.info(f"🔄 {regen_message}")

# -------------------------------
# Main generator page
# -------------------------------
def lesson_generator_page():
    show_logo()
    title_and_tagline()

    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")

        lesson_data['year_group'] = st.selectbox("Year Group",
            ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        lesson_data['ability_level'] = st.selectbox("Ability Level",
            ["Mixed ability","Lower ability","Higher ability"])
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration",
            ["30 min","45 min","60 min"])
        lesson_data['subject'] = st.text_input("Subject",
            placeholder="e.g. English, Maths, Science")
        lesson_data['topic'] = st.text_input("Topic",
            placeholder="e.g. Fractions, The Romans, Plant Growth")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)",
            placeholder="e.g. To understand fractions")
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)",
            placeholder="e.g. Visual aids, sentence starters")

        submitted = st.form_submit_button("🚀 Generate Lesson Plan")

    if submitted:
        prompt = f"""
Year Group: {lesson_data['year_group']}
Subject: {lesson_data['subject']}
Topic: {lesson_data['topic']}
Learning Objective: {lesson_data['learning_objective'] or 'Not specified'}
Ability Level: {lesson_data['ability_level']}
Lesson Duration: {lesson_data['lesson_duration']}
SEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}
"""
        st.session_state.last_prompt = prompt
        generate_and_display_plan(prompt, title="Original", lesson_data=lesson_data)

    # Regeneration options
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
            ]
        )
        custom_instruction = st.text_input(
            "Or type your own custom instruction (optional)",
            placeholder="e.g. Make it more interactive with outdoor activities"
        )
        if st.button("🔁 Regenerate Lesson Plan"):
            extra_instruction = custom_instruction if custom_instruction else regen_style
            new_prompt = st.session_state.last_prompt + "\n\n" + extra_instruction
            generate_and_display_plan(
                new_prompt,
                title=f"Regenerated {len(st.session_state.lesson_history)+1}",
                lesson_data=lesson_data
            )

# -------------------------------
# Sidebar history
# -------------------------------
def show_lesson_history():
    st.sidebar.title("📜 Lesson History")
    if st.session_state.lesson_history:
        for entry in reversed(st.session_state.lesson_history):
            with st.sidebar.expander(f"{entry['title']}"):
                st.markdown(f"<div class='stCard'>{entry['content']}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.write("No lesson history yet.")

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    show_lesson_history()
    lesson_generator_page()
