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

    # Remove standalone timing lines like "(5 minutes)"
    text = re.sub(r'^\(\d+\s*minutes?\)$', '', text, flags=re.MULTILINE)

    HEADER_KEYWORDS = [
        "Introduction",
        "Warm-Up Activity",
        "Main Activity",
        "Differentiation",
        "Assessment",
        "Resources",
        "Conclusion",
        "Closure",
        "Extension",
        "Extension Activities",
        "Reflection",
        "Plenary",
        "Starter",
        "Guided Practice",
        "Independent Practice"
    ]

    lines = [l.strip() for l in text.splitlines()]
    output = []

    def flush_blank():
        if output and output[-1] != "":
            output.append("")
for raw in lines:
    if not raw:
        continue

    matched_header = None
    for h in HEADER_KEYWORDS:
        if raw.lower().startswith(h.lower()):
            matched_header = h
            rest = raw[len(h):].strip(" :")
            
            # --- FORCE BLANK LINE BEFORE HEADER ---
            if output and output[-1] != "":
                output.append("")
            
            # --- ADD HEADER ---
            output.append(f"**{h}**")
            
            # --- FORCE BLANK LINE AFTER HEADER ---
            output.append("")
            
            # --- If there's text right after header, push as separate paragraph ---
            if rest:
                output.append(rest)
                output.append("")
            break

    if matched_header:
        continue

    # Bullet handling
    if raw.startswith(("-", "•", "*")) or raw[:2].isdigit():
        bullet = raw.lstrip("-•*0123456789. ").strip()
        output.append(f"- {bullet}")
        continue

    # Normal paragraph
    output.append(raw)

    final = []
    for line in output:
        if line.startswith("**") and line.endswith("**"):
            if final and final[-1] != "":
                final.append("")
            final.append(line)
            final.append("")
        else:
            final.append(line)

    cleaned = []
    for ln in final:
        if ln == "" and cleaned and cleaned[-1] == "":
            continue
        cleaned.append(ln)

    return "\n".join(cleaned).strip()
    
def count_words(text: str) -> int:
    if not text:
        return 0
    return len(text.split())

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
            unsafe_allow_html=True,
        )
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
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=14, spaceAfter=6)
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
# Generator (STRONGER INSTRUCTIONS + CLEANUP)
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message="", lesson_data=None):
    if lesson_data is None:
        lesson_data = {}

    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached. {daily_limit} lessons allowed per day.")
        return

    st.session_state.lesson_count += 1

    # Determine min words by lesson duration
    duration_map = {
        "30 min": 750,
        "45 min": 850,
        "60 min": 1000
    }
    min_words = duration_map.get(lesson_data.get('lesson_duration','30 min'), 750)

    # Show daily usage on top (keeps user expectation consistent)
    st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used — {daily_limit - st.session_state.lesson_count} left")

    # Strong generation instructions (prevents internal duplicated titles & repeated metadata)
    generation_instructions = (
        "\n\nImportant instructions for generation (must follow exactly):\n"
        "- Use British English only (e.g., 'colour', 'favour', 'maths').\n"
        "- Do NOT include emojis or emoji characters anywhere.\n"
        "- DO NOT output any internal lesson title lines such as 'Lesson Plan', 'Year 1 Maths Lesson Plan', 'Lesson Plan: ...' or similar anywhere inside the generated body.\n"
        "- DO NOT repeat the metadata fields (Lesson Title, Subject, Topic, Year Group, Duration, Ability Level, SEN/EAL Notes, Learning Objective) inside the body. Metadata is displayed separately in the app.\n"
        "- Start the generated content with the first section header (for example: 'Introduction'). Do NOT prepend a second title or metadata block.\n"
        "- Format headings as a single line header, followed by one blank line, then '-' bullet points or tight paragraph lines.\n"
        "- Collapse extra blank lines so there is at most one blank line between sections.\n"
        f"- Minimum length: {min_words} words. Maximum length: 1000 words.\n"
        "- Include clear timings, detailed activities, differentiation, assessment and resources.\n"
    )

    prompt_with_req = prompt + generation_instructions

    with st.spinner("✨ Creating lesson plan..."):
        try:
            attempts = 0
            final_output = None

            while attempts < 3:
                attempts += 1

                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_with_req}],
                    temperature=0.25,
                    max_tokens=2200,
                )

                raw = response.choices[0].message.content
                cleaned = clean_markdown(raw)
                formatted = format_tight_output(cleaned)
                wcount = count_words(formatted)

                if wcount >= min_words:
                    final_output = formatted
                    break
                else:
                    # If too short, request expansion (keeps the same guard rails)
                    prompt_with_req += (
                        "\n\nPlease expand the lesson plan with more detail, step-by-step examples, timings, differentiation, and assessment to reach the required word count."
                    )

            if final_output is None:
                final_output = formatted or ""

            # --- POST-PROCESSING CLEANUP (remove duplicates / stray titles) ---

            # 1) Remove any internal title lines (common patterns)
            final_output = re.sub(r'(?im)^\s*(lesson\s*plan[:\-]?.*)\s*$', '', final_output)
            final_output = re.sub(r'(?im)^\s*(year\s*\d+\s*.*lesson\s*plan[:\-]?.*)\s*$', '', final_output)
            final_output = re.sub(r'(?im)^\s*(lesson\s*plan\s*[:\-].*)\s*$', '', final_output)

            # 2) Remove duplicated heading labels (e.g., multiple "Learning Objective" headers)
            final_output = re.sub(r'(?im)(^\s*Learning\s*Objective\s*\n\s*)+', 'Learning Objective\n\n', final_output)

            # 3) Remove duplicated blank headers like "Introduction" followed immediately by another "Introduction" section
            final_output = re.sub(r'(?im)^\s*(Introduction\s*)\n\s*\1', r'Introduction', final_output)

            # Collapse any runs of more than two blank lines to exactly two
            final_output = re.sub(r'\n{3,}', '\n\n', final_output).strip()

            # Finally, ensure the content starts with a header (not an empty line)
            final_output = final_output.lstrip()

            # Convert bold markers to HTML <b> for preview
            final_output_html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', final_output)

            # Remove any leading "Lesson Title: ..." lines that the model may have included earlier (extra safety)
            final_output_html = re.sub(r'(?im)^\s*lesson\s*title:.*(?:<br>)?\s*', '', final_output_html.strip(), flags=re.M)

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

            # Exports
            pdf_buffer = create_pdf(final_output)
            docx_buffer = create_docx(final_output)

            st.markdown(
                f"""
<div style="display:flex; gap:10px; margin-top:16px; flex-wrap:wrap;">
    <a href="data:text/plain;base64,{base64.b64encode(final_output.encode()).decode()}" download="lesson_plan.txt">
        <button style="padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ TXT</button>
    </a>
    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
        <button style="padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ PDF</button>
    </a>
    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
        <button style="padding:16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ DOCX</button>
    </a>
</div>
""",
                unsafe_allow_html=True
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
