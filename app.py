# -------------------------------
# App.py - LessonLift (Titles + Duplication Fully Fixed + Proper Downloads)
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
# TEXT CLEANING
# -------------------------------
def clean_markdown(text) -> str:
    if text is None:
        return ""
    text = str(text)

    text = re.sub(
        r"^(lesson plan|year \d.*lesson|lesson\s*plan.*|.*?shapes.*?)$",
        "",
        text,
        flags=re.I | re.M
    )
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
        "Learning Objective", "Lesson Duration", "Classroom Setup",
        "Introduction", "Main Activity", "Differentiation", "Assessment",
        "Closure", "Conclusion", "Resources Needed", "Reflection",
        "Examples", "Shape Hunt", "Shape Sorting"
    ]

    lines = text.splitlines()
    result = []
    seen_headers = set()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line == "":
            if len(result) == 0 or result[-1] == "":
                i += 1
                continue
            result.append("")
            i += 1
            continue

        is_header = False
        for kw in header_keywords:
            if re.match(rf"^{re.escape(kw)}\b", line, flags=re.I):
                header_clean = kw
                if header_clean.lower() in seen_headers:
                    i += 1
                    continue
                seen_headers.add(header_clean.lower())
                result.append(f"**{header_clean}**")
                result.append("")
                is_header = True
                break

        if is_header:
            i += 1
            continue

        if line.startswith("-"):
            result.append(f"- {line[1:].strip()}")
        else:
            result.append(line)

        i += 1

    final = []
    for ln in result:
        if ln == "" and (len(final) == 0 or final[-1] == ""):
            continue
        final.append(ln)

    return "\n".join(final).strip()

def count_words(text: str) -> int:
    if not text:
        return 0
    return len(re.findall(r'\w+', text))

# -------------------------------
# Logo + Title
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
    except:
        st.warning("Logo file not found. Upload 'logo.png'.")

def title_and_tagline():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

# -------------------------------
# PDF Exporter
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        'NormalFixed',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        spaceAfter=6
    )

    story = []
    for line in text.splitlines():
        if not line.strip():
            story.append(Spacer(1, 6))
        else:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe)
            story.append(Paragraph(safe, normal))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# DOCX Exporter
# -------------------------------
def create_docx(text):
    doc = Document()
    for line in text.splitlines():
        header_match = re.match(r'^\*\*(.+?)\*\*$', line.strip())
        if header_match:
            p = doc.add_paragraph()
            run = p.add_run(header_match.group(1))
            run.bold = True
        elif line.strip() == "":
            doc.add_paragraph()
        else:
            doc.add_paragraph(line.rstrip())

    b = BytesIO()
    doc.save(b)
    b.seek(0)
    return b

# -------------------------------
# GENERATE + DISPLAY
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message="", lesson_data=None):
    if lesson_data is None:
        lesson_data = {}

    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached ({daily_limit}/day).")
        return

    st.session_state.lesson_count += 1

    st.info(
        f"📊 {st.session_state.lesson_count}/{daily_limit} used — "
        f"{daily_limit - st.session_state.lesson_count} left"
    )

    ai_rules = """
Important instructions for the AI:
- Use British English only.
- No emojis.
- NEVER add your own title such as "Lesson Plan: ..." or "Year 1 Maths Lesson ...".
- DO NOT repeat the Learning Objective section.
- Allowed bold headers only: Learning Objective, Lesson Duration, Classroom Setup, Introduction, Main Activity, Shape Hunt, Shape Sorting, Differentiation, Assessment, Closure, Conclusion, Resources Needed, Reflection, Examples.
- Ensure perfect spacing: exactly one blank line after every header.
- 750–1000 words.
"""
    full_prompt = prompt + ai_rules

    with st.spinner("✨ Creating lesson plan..."):
        try:
            retries = 0
            final_output = None

            while retries < 2:
                retries += 1
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.3,
                    max_tokens=2200,
                )

                raw = response.choices[0].message.content
                cleaned = clean_markdown(raw)
                formatted = format_tight_output(cleaned)

                if count_words(formatted) >= 650:
                    final_output = formatted
                    break

                full_prompt += "\n\nPlease add more detail, explanations, examples, differentiation, and assessment depth."

            if final_output is None:
                final_output = formatted

            html_output = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', final_output)

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
    {html_output.replace("\\n","<br>").strip()}
</div>
"""
            st.markdown(metadata_html, unsafe_allow_html=True)

            # --------------------------
            # STREAMLIT DOWNLOAD BUTTONS
            # --------------------------
            pdf_file = create_pdf(final_output)
            docx_file = create_docx(final_output)
            txt_data = final_output.encode()

            st.download_button("⬇ Download TXT", txt_data, file_name="lesson_plan.txt")
            st.download_button("⬇ Download PDF", pdf_file, file_name="lesson_plan.pdf", mime="application/pdf")
            st.download_button("⬇ Download DOCX", docx_file, file_name="lesson_plan.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")
            return

    st.session_state.lesson_history.append({"title": title, "content": final_output})
    if regen_message:
        st.info(f"🔄 {regen_message}")

# -------------------------------
# UI PAGE
# -------------------------------
def lesson_generator_page():
    show_logo()
    title_and_tagline()

    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")

        lesson_data['year_group'] = st.selectbox("Year Group",
            ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])

        lesson_data['ability_level'] = st.selectbox("Ability Level",
            ["Mixed ability", "Lower ability", "Higher ability"])

        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration",
            ["30 min", "45 min", "60 min"])

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
            extra_instruction = custom_instruction or regen_style
            new_prompt = st.session_state.last_prompt + "\n\n" + extra_instruction

            generate_and_display_plan(
                new_prompt,
                title=f"Regenerated {len(st.session_state.lesson_history)+1}",
                lesson_data=lesson_data
            )

# -------------------------------
# Sidebar History
# -------------------------------
def show_lesson_history():
    st.sidebar.title("📜 Lesson History")
    if st.session_state.lesson_history:
        for entry in reversed(st.session_state.lesson_history):
            with st.sidebar.expander(f"{entry['title']}"):
                st.markdown(f"<div class='stCard'>{entry['content']}</div>",
                            unsafe_allow_html=True)
    else:
        st.sidebar.write("No lesson history yet.")

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    show_lesson_history()
    lesson_generator_page()
