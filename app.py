# -------------------------------
# App.py - LessonLift with OpenAI 1.0+ integration (final)
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

/* Main scrollable lesson plan box */
.stCard {
    background-color: #f9f9f9 !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 12px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.45em; /* slightly tighter for closer spacing */
    white-space: pre-wrap;
    max-height: 70vh;
    overflow-y: auto;
    font-size: 16px !important;  /* consistent font size */
    font-weight: 500 !important; /* normal weight for text */
}

/* Metadata at top of lesson plan (Lesson Title, Subject, Topic, etc.) */
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
# OpenAI API key from secrets
# -------------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# -------------------------------
# CLEAN & FORMAT FUNCTIONS
# -------------------------------
def clean_markdown(text) -> str:
    """
    Normalise output text:
    - Ensure it's a string
    - Remove markdown headings (#)
    - Replace bold/italic markers with plain text
    - Convert bullet chars to simple dashes
    - Collapse many blank lines into single blank line (tight spacing)
    - Trim leading/trailing whitespace
    """
    if text is None:
        return ""
    # Ensure string
    text = str(text)

    # Remove markdown headings markers (leading #s)
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove bold/italic markers but keep content
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)

    # Replace bullet characters with dash + single space
    text = text.replace("•", "-")
    text = text.replace("•", "-")
    text = re.sub(r'^[\t\s]*[\*\u2022]\s+', '- ', text, flags=re.MULTILINE)
    # replace other bullet variants
    text = re.sub(r'^[\t\s]*[-–—•]\s+', '- ', text, flags=re.MULTILINE)

    # Remove repeated long dashes (em-dash separators)
    text = re.sub(r'\-{3,}', '', text)

    # Collapse 3+ newlines into a single blank line (tight spacing)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Also replace any occurrence of two or more newlines with exactly ONE blank line
    text = re.sub(r'\n{2,}', '\n\n', text)

    # Trim whitespace on each line and then rejoin
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines).strip()

    return text

def format_tight_output(text: str) -> str:
    """
    Post-process to:
    - Wrap section headers in **bold** for preview (e.g., Introduction, Materials Needed).
    - Ensure headers have exactly one blank line after them.
    - Ensure bullets are '- ' and properly indented (no extraneous blank lines).
    - Keep everything tight (single blank line between sections).
    """
    if not text:
        return ""

    # Identify common header keywords to bold
    header_keywords = [
        "Learning Objective", "Learning Objectives", "Lesson Duration", "Topic",
        "Year Group", "Subject", "Ability Level", "SEN/EAL Notes",
        "Materials Needed", "Resources", "Resources Needed",
        "Lesson Outline", "Lesson Structure", "Introduction", "Main Activity",
        "Direct Instruction", "Guided Practice", "Independent Practice",
        "Closing", "Conclusion", "Assessment", "Differentiation",
        "Extension", "Reflection", "Homework", "Plenary", "Starter"
    ]

    lines = text.splitlines()
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # If empty, just append a single blank line only if previous line wasn't blank
        if line == "":
            if len(out_lines) == 0 or out_lines[-1].strip() != "":
                out_lines.append("")  # single blank line
            i += 1
            continue

        # Normalize bullets: if line starts with dash or number bullet, keep '- ' prefix
        m_bullet = re.match(r'^(?:\d+\.\s+)?[-–—•*]?\s*(.*)', line)
        # But we only want to convert lines that actually look like bullets when original started with bullet chars
        # We'll instead detect explicit leading '-' or '*' or '•' or numbered lines
        if re.match(r'^[\-\*\u2022]\s+', lines[i]) or re.match(r'^\d+\.\s+', lines[i]):
            content = re.sub(r'^[\-\*\u2022]?\s*', '', lines[i]).strip()
            out_lines.append(f"- {content}")
            i += 1
            continue

        # If line looks like a header (exact or startswith header keywords)
        is_header = False
        for kw in header_keywords:
            # match case-insensitive startswith or exact line, allow ":" at end
            if re.match(rf'^{re.escape(kw)}\s*:?\s*$', line, flags=re.I):
                is_header = True
                header_text = kw  # use canonical
                break
            # Also if line exactly equals kw with parentheses like "Introduction (5 minutes)"
            if re.match(rf'^{re.escape(kw)}\b', line, flags=re.I):
                # ensure it's not a long sentence (limit 5-7 words)
                if len(line.split()) <= 10:
                    is_header = True
                    header_text = line
                    break

        if is_header:
            # Bold the header for preview. Keep the original parenthetical if present.
            out_lines.append(f"**{header_text.strip()}**")
            # Ensure exactly one blank line after header (if next non-empty line isn't blank)
            # Skip any extra blank lines in the source
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            # Move i to next non-empty line
            i = j
            # Add a single blank line to separate header from body (but not at end)
            if i < len(lines):
                out_lines.append("")
            continue

        # Otherwise treat it as a normal paragraph line; preserve it
        # If it begins with '-', keep it as bullet (ensured above)
        out_lines.append(line)
        i += 1

    # Final join ensuring no more than one blank line in a row
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
    """
    Create PDF using Helvetica (avoid DejaVu/emoji font mapping issues).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    # Use Helvetica to avoid font mapping issues with unknown glyphs
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=14, spaceAfter=6)
    story = []
    for line in text.splitlines():
        if not line.strip():
            story.append(Spacer(1,6))
        else:
            # Escape special chars for xml
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            # Convert bold markers (**) to simple bold tag for PDF
            # ReportLab allows simple <b> tags
            safe = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe)
            story.append(Paragraph(safe, normal))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for line in text.splitlines():
        # If bold header detected **Header**, add run with bold
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
# Generator
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached. {daily_limit} lessons allowed per day.")
        return

    st.session_state.lesson_count += 1

    # Append strict generation requirements (UK English, no emojis, tight format, word count)
    generation_instructions = (
        "\n\nImportant instructions for generation:\n"
        "- Use British English spelling only (e.g., 'colour', 'favour', 'maths').\n"
        "- Do NOT include emojis or special emoji characters anywhere.\n"
        "- Format exactly: Section Title (bold in preview), single blank line, then dash '-' bullet points or tight paragraph lines.\n"
        "- Tight spacing: collapse extra blank lines so there is at most one blank line between sections/paragraphs.\n"
        "- Minimum length: 750 words. Maximum length: 1000 words.\n"
        "- Include these fields at the top: Lesson Title, Subject, Topic, Year Group, Lesson Duration, Ability Level, SEN/EAL Notes, Learning Objective (short), then 'Lesson Outline' and sections.\n"
    )

    prompt_with_req = prompt + generation_instructions

    with st.spinner("✨ Creating lesson plan..."):
        try:
            # Attempt generation up to 2 times if word count too low
            attempts = 0
            final_output = None
            while attempts < 2:
                attempts += 1
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt_with_req}],
                    temperature=0.3,
                    max_tokens=2200,
                )
                output = response.choices[0].message.content
                # Clean & format
                cleaned = clean_markdown(output)
                formatted = format_tight_output(cleaned)
                wcount = count_words(formatted)

                if wcount >= 750:
                    final_output = formatted
                    break
                else:
                    # If too short, ask model to expand (append an instruction) and retry once
                    prompt_with_req += "\n\nPlease expand the plan with more detail, examples, differentiation and assessment to reach at least 750 words. Use British English and keep format tight."

            if final_output is None:
                final_output = formatted

            # Final safety: ensure no emoji characters remain
            final_output = re.sub(r'[\U00010000-\U0010ffff]', '', final_output)
            final_output = final_output.replace("🛠️", "").replace("✨", "").replace("✅", "").replace("📝", "").replace("⚡", "").replace("🤝", "")

            # Save to history
            st.session_state.lesson_history.append({"title": title, "content": final_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            remaining_today = daily_limit - st.session_state.lesson_count
            st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used — {remaining_today} left")

            # Metadata + Lesson preview with tight formatting
            metadata_html = f"""
<div class='stCard'>
    <div class='metadata-line'><b>Lesson Title:</b> {title}</div>
    <div class='metadata-line'><b>Subject:</b> {lesson_data.get('subject','')}</div>
    <div class='metadata-line'><b>Topic:</b> {lesson_data.get('topic','')}</div>
    <div class='metadata-line'><b>Year Group:</b> {lesson_data.get('year_group','')}</div>
    <div class='metadata-line'><b>Duration:</b> {lesson_data.get('lesson_duration','')}</div>
    <div class='metadata-line'><b>Ability Level:</b> {lesson_data.get('ability_level','')}</div>
    <div class='metadata-line'><b>SEN/EAL Notes:</b> {lesson_data.get('sen_notes','None')}</div>
    <br>
    {final_output.replace('\\n','<br>')}
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
        <button style="padding:16px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ TXT</button>
    </a>
    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
        <button style="padding:16px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ PDF</button>
    </a>
    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
        <button style="padding:16px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ DOCX</button>
    </a>
</div>
""",
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")
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
Lesson Title: {lesson_data['topic'] or 'Lesson'}
Year Group: {lesson_data['year_group']}
Subject: {lesson_data['subject'] or 'Not specified'}
Topic: {lesson_data['topic'] or 'Not specified'}
Lesson Duration: {lesson_data['lesson_duration']}
Ability Level: {lesson_data['ability_level']}
SEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}
Learning Objective: {lesson_data['learning_objective'] or 'Not specified'}
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
            ]
        )
        custom_instruction = st.text_input(
            "Or type your own custom instruction (optional)",
            placeholder="e.g. Make it more interactive with outdoor activities"
        )
        if st.button("🔁 Regenerate Lesson Plan"):
            extra_instruction = custom_instruction if custom_instruction else regen_style
            new_prompt = st.session_state.last_prompt + "\n\n" + extra_instruction
            generate_and_display_plan(new_prompt, title=f"Regenerated {len(st.session_state.lesson_history)+1}")

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
