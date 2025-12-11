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

st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

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

openai.api_key = st.secrets.get("OPENAI_API_KEY")

def clean_markdown(text) -> str:
    if text is None:
        return ""
    text = str(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = text.replace("•", "-")
    text = re.sub(r'^[\t\s]*[-–—•]\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()

def format_lesson_output(text: str) -> str:
    if not text:
        return ""
    header_keywords = [
        "Learning Objective", "Lesson Duration", "Classroom Setup", "Introduction", 
        "Discussion Points", "Main Activity", "Sorting Activity", "Hands-On Exploration", 
        "Practical Application", "Assessment", "Independent Practice", "Conclusion",
        "Follow-Up Activities", "Extension Activities", "Resources Needed", "Differentiation"
    ]
    lines = text.splitlines()
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "":
            if len(out_lines) == 0 or out_lines[-1].strip() != "":
                out_lines.append("")
            i += 1
            continue
        is_header = any(re.match(rf'^{re.escape(kw)}\b', line, flags=re.I) for kw in header_keywords)
        if is_header:
            out_lines.append(f"{line}")
            out_lines.append("")
            i += 1
            continue
        if line.startswith("-"):
            content = line[1:].strip()
            out_lines.append(f"- {content}")
        else:
            out_lines.append(line)
        i += 1
    final_text = []
    for ln in out_lines:
        if ln == "" and (len(final_text) == 0 or final_text[-1] == ""):
            continue
        final_text.append(ln)
    return "\n".join(final_text).strip()

def count_words(text: str) -> int:
    if not text:
        return 0
    return len(re.findall(r'\w+', text))

# Preview & downloads functions (PDF/DOCX/TXT)
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=14, spaceAfter=6)
    story = []
    for line in text.splitlines():
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
    for line in text.splitlines():
        header_match = re.match(r'^(.+)$', line.strip())
        if header_match:
            p = doc.add_paragraph()
            run = p.add_run(header_match.group(1))
            run.bold = True
        elif line.strip() == "":
            doc.add_paragraph()
        else:
            doc.add_paragraph(line.rstrip())
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# Generator

def generate_and_display_plan(prompt, title="Latest", lesson_data=None):
    if lesson_data is None:
        lesson_data = {}
    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached. {daily_limit} lessons allowed per day.")
        return
    st.session_state.lesson_count += 1

    st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used — {daily_limit - st.session_state.lesson_count} left")

    prompt_with_req = f"{prompt}\n\nGenerate a highly detailed, word-count appropriate lesson plan (30min~750w, 45min~850w, 60min~1000w) in UK English, with bold headings, perfect spacing, aligned bullet points, no duplication."

    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_with_req}],
                temperature=0.3,
                max_tokens=2200,
            )
            raw = response.choices[0].message.content
            cleaned = clean_markdown(raw)
            formatted = format_lesson_output(cleaned)

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
    {formatted.replace('\n','<br>').strip()}
</div>
"""
            st.markdown(metadata_html, unsafe_allow_html=True)

            pdf_buffer = create_pdf(formatted)
            docx_buffer = create_docx(formatted)
            st.markdown(f"""
<div style='display:flex; gap:10px; margin-top:16px; flex-wrap:wrap;'>
    <a href='data:text/plain;base64,{base64.b64encode(formatted.encode()).decode()}' download='lesson_plan.txt'>
        <button style='padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;'>⬇ TXT</button>
    </a>
    <a href='data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}' download='lesson_plan.pdf'>
        <button style='padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;'>⬇ PDF</button>
    </a>
    <a href='data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}' download='lesson_plan.docx'>
        <button style='padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;'>⬇ DOCX</button>
    </a>
</div>
""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")
            return

# Main generator page

def lesson_generator_page():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate detailed UK primary school lesson plans quickly!")
    lesson_data = {}
    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
        lesson_data['subject'] = st.text_input("Subject", placeholder="e.g. Maths, Science")
        lesson_data['topic'] = st.text_input("Topic", placeholder="e.g. Shapes, Fractions")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)", placeholder="e.g. Identify basic shapes")
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, peer support")
        submitted = st.form_submit_button("🚀 Generate Lesson Plan")
    if submitted:
        prompt = f"Year Group: {lesson_data['year_group']}\nSubject: {lesson_data['subject']}\nTopic: {lesson_data['topic']}\nLearning Objective: {lesson_data['learning_objective'] or 'Not specified'}\nAbility Level: {lesson_data['ability_level']}\nLesson Duration: {lesson_data['lesson_duration']}\nSEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}"
        st.session_state.last_prompt = prompt
        generate_and_display_plan(prompt, title="Original", lesson_data=lesson_data)

# Sidebar

def show_lesson_history():
    st.sidebar.title("📜 Lesson History")
    if st.session_state.lesson_history:
        for entry in reversed(st.session_state.lesson_history):
            with st.sidebar.expander(f"{entry['title']}"):
                st.markdown(f"<div class='stCard'>{entry['content']}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.write("No lesson history yet.")

if __name__ == "__main__":
    show_lesson_history()
    lesson_generator_page()
