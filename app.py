# -------------------------------
# App.py - LessonLift with OpenAI 1.0+ integration
# (updated: fixed preview spacing, unified bullets to '-', PDF without emojis)
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
    padding: 16px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.45em;
    white-space: pre-wrap;
    max-height: 70vh;
    overflow-y: auto;
    font-size: 14px;
}
.stSmall {
    font-size:13px;
    color:#555;
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
# Text cleaning & formatting helpers
# -------------------------------
def clean_markdown(text: str) -> str:
    """Normalize incoming model text, remove markdown headers/bold/italics, collapse excessive blank lines."""
    if text is None:
        return ""
    # Ensure string
    text = str(text)

    # Remove markdown headers like ### or ##
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Replace bold/italic markup
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)

    # Remove table-like lines
    text = re.sub(r'\|.*?\|', '', text)

    # Replace bullets such as •, * or • with '-'
    text = normalize_bullets(text)

    # Replace long runs of hyphens (e.g., ---) with a single dash line removed
    text = re.sub(r'-{3,}', '', text)

    # Normalize Windows CRLF
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Collapse 3+ newlines into 2 (one blank line)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Trim spaces at start/end of each line and collapse multiple spaces
    lines = [re.sub(r'[ \t]+', ' ', ln).strip() for ln in text.splitlines()]
    text = "\n".join(lines).strip()

    # Final collapse: ensure at most one blank line between blocks
    text = re.sub(r'\n{2,}', '\n\n', text)

    return text

def normalize_bullets(text: str) -> str:
    """Convert various bullet types to '- ' and convert numbered lists to '1.' keep as is."""
    # Replace bullet characters with '- '
    text = re.sub(r'^[\s]*[•\u2022\*]+\s+', '- ', text, flags=re.MULTILINE)
    # Replace bolded bullets like "**-** " or "**•** " etc.
    text = re.sub(r'\*\s*[\u2022\*-\+]\s*\*', '- ', text)
    # Replace lines that start with '- -' or '—' with '-'
    text = re.sub(r'^[\s]*[-–—]{2,}\s*', '- ', text, flags=re.MULTILINE)
    return text

# Emoji removal for PDF (common emoji ranges)
def remove_emoji(text: str) -> str:
    if text is None:
        return ""
    # Wide emoji regex covering the main ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F000-\U0001F9FF"  # emoticons / symbols
        "\U00002600-\U000027BF"  # Misc symbols
        "\U0001F300-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def format_for_preview_html(text: str) -> str:
    """
    Convert cleaned text into compact HTML for the scrollable preview.
    - Keeps one blank line between sections
    - Converts lines starting with '- ' into nicely indented bullets (using '-' as requested)
    - Avoids huge gaps
    """
    if not text:
        return ""
    # Ensure clean
    text = clean_markdown(text)

    # Split into paragraphs (blocks separated by one blank line)
    parts = text.split('\n\n')
    html_parts = []
    for p in parts:
        lines = p.splitlines()
        # If it's a multi-line paragraph and lines start with '- ' treat as bullet block
        if all(ln.strip().startswith('- ') or re.match(r'^\d+\.', ln.strip()) for ln in lines if ln.strip()):
            # convert each bullet line into a div with small margin
            bullets = []
            for ln in lines:
                ln = ln.strip()
                if not ln:
                    continue
                # numbered lists keep digits; other bullets start with '- '
                if re.match(r'^\d+\.', ln):
                    bullets.append(f"<div style='margin-left:6px; margin-bottom:4px;'>{ln}</div>")
                else:
                    # ensure single '- ' prefix
                    content = ln[2:].strip() if ln.startswith('- ') else ln
                    bullets.append(f"<div style='margin-left:12px; margin-bottom:4px;'>- {escape_html(content)}</div>")
            html_parts.append("".join(bullets))
        else:
            # Regular paragraph, show each line as separate line inside paragraph
            escaped = "<br>".join(escape_html(ln) for ln in lines if ln.strip() != "")
            if escaped:
                html_parts.append(f"<div style='margin-bottom:8px;'>{escaped}</div>")
    return "".join(html_parts)

def escape_html(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))

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
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:16px;">
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
def create_pdf(text: str):
    """
    Create a PDF buffer. For PDF we remove emojis (to avoid font boxes) and keep formatting neat.
    """
    text_no_emoji = remove_emoji(text)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=6)
    story = []
    for raw in text_no_emoji.splitlines():
        line = raw.rstrip()
        if not line.strip():
            story.append(Spacer(1,6))
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, normal))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text: str):
    """
    Create a DOCX buffer. DOCX will contain emojis (if present).
    """
    doc = Document()
    for raw in text.splitlines():
        doc.add_paragraph(raw.rstrip())
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

    with st.spinner("✨ Creating lesson plan..."):
        try:
            # NOTE: We kept your existing call pattern to avoid changing other behaviours.
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
            )
            # Access response safely
            output = ""
            try:
                output = response.choices[0].message.content
            except Exception:
                # fallback if structure differs
                output = getattr(response.choices[0], "text", "") or str(response)

            # Add emojis to section headers automatically for preview & TXT/DOCX (keeps as you liked)
            # Only add emoji markers where those words exist as headings to avoid accidental replacements in running text.
            # Use word boundaries to avoid mid-word replacements.
            output = re.sub(r'\bIntroduction\b', '✨ Introduction', output)
            output = re.sub(r'\bMain Activity\b', '🛠️ Main Activity', output)
            output = re.sub(r'\bClosing Activity\b', '✅ Closing Activity', output)
            output = re.sub(r'\bAssessment\b', '📝 Assessment', output)
            output = re.sub(r'\bExtension\b', '⚡ Extension Activity', output)
            output = re.sub(r'\bSupport\b', '🤝 Support', output)

            # Clean and normalize bullets/spacing
            clean_output = clean_markdown(output)

            # Save to history (keeps emojis in history)
            st.session_state.lesson_history.append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            remaining_today = daily_limit - st.session_state.lesson_count
            st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used — {remaining_today} left")

            # Display title + formatted preview (HTML inside scrollable card)
            st.markdown(f"### 📖 {title}")
            preview_html = format_for_preview_html(clean_output)
            if not preview_html:
                preview_html = "<div class='stCard'>No content returned.</div>"
            else:
                preview_html = f"<div class='stCard'>{preview_html}</div>"
            st.markdown(preview_html, unsafe_allow_html=True)

            # Prepare downloadable files
            pdf_buffer = create_pdf(clean_output)   # PDF without emojis
            docx_buffer = create_docx(clean_output) # DOCX with emojis
            txt_data = clean_output

            st.markdown(
                f"""
                <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                    <a href="data:text/plain;base64,{base64.b64encode(txt_data.encode()).decode()}" download="lesson_plan.txt">
                        <button style="padding:10px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                        <button style="padding:10px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ PDF</button>
                    </a>
                    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
                        <button style="padding:10px 16px; background:#4CAF50; color:white; border:none; border-radius:8px;">⬇ DOCX</button>
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
                st.markdown(f"<div class='stCard'>{format_for_preview_html(entry['content'])}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.write("No lesson history yet.")

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    show_lesson_history()
    lesson_generator_page()
