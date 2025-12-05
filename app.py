# -------------------------------
# App.py - LessonLift with OpenAI 1.0+ integration (final + bullet/header fix)
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
    header_keywords = [
        "Learning Objective", "Lesson Duration", "Ability Level", "SEN/EAL Notes",
        "Introduction", "Main Activity", "Shape Hunt", "Shape Sorting",
        "Conclusion", "Assessment", "Differentiation", "Extension Activities",
        "Resources Needed", "Plenary", "Starter"
    ]
    lines = text.splitlines()
    out_lines = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            if len(out_lines) == 0 or out_lines[-1].strip() != "":
                out_lines.append("")
            i += 1
            continue

        # Section header
        is_header = any(line.lower().startswith(kw.lower()) for kw in header_keywords)
        if is_header:
            out_lines.append(f"**{line}**")
            out_lines.append("")
            i += 1
            continue

        # Bullets
        if re.match(r'^[-\*\u2022]\s+', line) or re.match(r'^\d+\.\s+', line):
            content = re.sub(r'^[-\*\u2022]?\s*', '', line).strip()
            out_lines.append(f"- {content}")
        else:
            # Wrapped line for previous bullet
            if out_lines and out_lines[-1].startswith("- "):
                out_lines.append("  " + line)
            else:
                out_lines.append(line)
        i += 1

    # Remove consecutive blank lines
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

# -------------------------------
# Logo + title
# -------------------------------
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:12px;">
                <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
                    <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;" />
                </div>
            </div>
            """,
            unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png'.")

def title_and_tagline():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

# -------------------------------
# Exporters
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, leading=14, spaceAfter=6)
    story = []
    for line in text.splitlines():
        if not line.strip():
            story.append(Spacer(1,6))
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            safe = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe)
            story.append(Paragraph(safe, normal))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for line in text.splitlines():
        header_match = re.match(r'^\*\*(.+)\*\*$', line.strip())
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

# -------------------------------
# Generator (final)
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message="", lesson_data=None):
    if lesson_data is None:
        lesson_data = {}

    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached. {daily_limit} lessons allowed per day.")
        return
    st.session_state.lesson_count += 1

    generation_instructions = (
        "\n\nImportant instructions:\n"
        "- British English only.\n"
        "- No emojis.\n"
        "- Section Title (bold), one blank line, then '-' bullet points.\n"
        "- Remove extra blank lines.\n"
        "- 750–1000 words.\n"
    )

    prompt_with_req = prompt + generation_instructions

    with st.spinner("✨ Creating lesson plan..."):
        try:
            attempts = 0
            final_output = None
            while attempts < 2:
                attempts += 1
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_with_req}],
                    temperature=0.3,
                    max_tokens=2200
                )
                raw = response.choices[0].message.content
                cleaned = clean_markdown(raw)
                formatted = format_tight_output(cleaned)
                if count_words(formatted) >= 750:
                    final_output = formatted
                    break
                prompt_with_req += "\n\nPlease expand with more detail, differentiation, examples, and assessment."

            if final_output is None:
                final_output = formatted

            final_output_html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', final_output)
            final_output_html = re.sub(r'(?i)^\s*lesson\s*title:.*(?:<br>)?\s*', '', final_output_html.strip(), flags=re.M)
            final_output_html = re.sub(r'^\s*(?:<br>\s*)+', '', final_output_html)

            # -------------------------------
            # Metadata + Lesson preview
            # -------------------------------
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
    {final_output_html.replace('\\n','<br>').strip()}
</div>
"""
            st.markdown(metadata_html, unsafe_allow_html=True)

            pdf_buffer = create_pdf(final_output)
            docx_buffer = create_docx(final_output)

            st.markdown(f"""
<div style="display:flex; gap:10px; margin-top:16px; flex-wrap:wrap;">
    <a href="data:text/plain;base64,{base64.b64encode(final_output.encode()).decode()}" download="lesson_plan.txt">
        <button style="padding:16px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ TXT</button>
    </a>
    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
        <button style="padding:16px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ PDF</button>
    </a>
    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
        <button style="padding:16px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ DOCX</button>
    </a>
</div>
""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")
            return

    st.session_state.lesson_history.append({"title": title, "content": final_output})
    if regen_message:
        st.info(f"🔄 {regen_message}")

    remaining_today = daily_limit - st.session_state.lesson_count
    st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used — {remaining_today} left")

# -------------------------------
# Main generator page
# -------------------------------
def lesson_generator_page():
    show_logo()
    title_and_tagline()
    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
        lesson_data['subject'] = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
        lesson_data['topic'] = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions")
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters")

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
