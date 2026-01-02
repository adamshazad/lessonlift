# -------------------------------
# App.py - LessonLift with OpenAI 1.0+ integration (fixed)
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
    margin-top: 2px;
    margin-bottom: 2px;
}

.metadata-line:last-child {
    margin-bottom: 14px;
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
# Helper: clean + format functions
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
    return "\n".join([line.rstrip() for line in text.splitlines()]).strip()

def format_tight_output(text: str) -> str:
    if not text:
        return ""
    HEADER_KEYWORDS = [
    "Introduction", "Warm-Up Activity", "Starter Activity", "Hook", "Engagement Activity",
    "Lesson Outline", "Lesson Plan", "Lesson Structure", "Lesson Flow", 
    "Direct Instruction", "Main Activity", "Guided Practice",
    "Independent Work", "Pair Work", "Collaborative Task", "Group Work", "Group Discussion",
    "Practical Activity", "Hands-On Activity", "Interactive Session", "Interactive Activity",
    "Activity 1", "Activity 2", "Activity 3", "Activity 4", "Activity 5", "Step-by-Step Activity",
    "Task Instructions", "Learning Activities", "Activities", "Activity Overview",
    "Lesson Goals", "Learning Objective", "Learning Objectives", "Objectives",
    "Success Criteria", "Key Points", "Main Points", "Learning Points", "Notes",
    "Check Understanding", "Question and Answer", "Q&A", "Discussion", "Feedback",
    "Peer Assessment", "Self-Assessment", "Assessment", "Assessment Task",
    "Reflection and Assessment", "Consolidation and Assessment", "Closure", 
    "Closure and Reflection", "Closing Activity", "Closing Remarks", "Plenary", "Recap",
    "Review", "Summary", "Lesson Summary", "Exit Ticket", "Next Steps",
    "Differentiation", "Extension Activity", "Extra Challenge", "Follow-Up Activity",
    "Homework", "Resources", "Materials Needed", "Equipment", "Instructions",
    "Practice", "Skill Practice", "Guided Activities", "Independent Activities",
    "Pair Activities", "Group Activities", "Collaborative Activities",
    "Interactive Learning", "Engagement Task", "Starter Task", "Introduction Task",
    "Lesson Introduction", "Activity Instructions", "Learning Task", "Task Overview",
    "Learning Session", "Instructional Activity", "Teaching Points", "Lesson Points",
    "Lesson Notes", "Learning Notes", "Lesson Content", "Content Overview",
    "Content Summary", "Lesson Recap", "Activity Recap", "Session Recap",
    "Session Summary", "Learning Recap", "Learning Reflection", "Reflection",
    "Student Reflection", "Teacher Reflection", "Guided Session", "Structured Activity",
    "Independent Session", "Group Session", "Collaborative Session", "Practical Session",
    "Interactive Practice", "Interactive Task", "Task Practice", "Skill Task",
    "Learning Practice", "Review Activity", "Lesson Review", "Activity Review",
    "Formative Assessment", "Summative Assessment", "Evaluation", "Assessment Overview",
    "Assessment Notes", "Lesson Evaluation", "Task Evaluation", "Student Evaluation",
    "Observation Notes", "Observation Activity", "Learning Evidence", "Learning Outcomes",
    "Lesson Outcomes", "Activity Outcomes", "Achievement Criteria", "Success Indicators",
    "Starter Discussion", "Engagement Discussion", "Introduction Discussion",
    "Closing Discussion", "Main Discussion", "Group Reflection", "Class Discussion",
    "Exit Reflection", "Session Closure", "Session Conclusion", "Lesson Closure",
    "Interactive Exercise", "Exercise 1", "Exercise 2", "Exercise 3", "Exercise 4",
    "Exercise 5", "Hands-On Exercise", "Practical Exercise", "Task Exercise", "Learning Exercise",
    "Guided Exercise", "Independent Exercise", "Collaborative Exercise", "Pair Exercise",
    "Assessment Exercise", "Follow-Up Exercise", "Extension Exercise", "Extra Exercise",
    "Starter Exercise", "Closure Exercise", "Engagement Exercise", "Recap Exercise",
    "Review Exercise", "Reflection Exercise", "Plenary Exercise", "Exit Exercise",
    "Lesson Activity", "Lesson Task", "Activity Task", "Teaching Activity", "Learning Activity",
    "Instruction Activity", "Interactive Lesson", "Session Activity", "Lesson Interaction",
    "Teaching Session", "Learning Session", "Student Activity", "Student Task", "Student Exercise",
    "Pair Activity", "Pair Task", "Group Task", "Group Exercise", "Collaborative Task",
    "Collaborative Exercise", "Independent Task", "Independent Exercise", "Practice Task",
    "Skill Development", "Skill Building", "Knowledge Check", "Understanding Check",
    "Comprehension Activity", "Skill Assessment", "Knowledge Assessment", "Learning Assessment",
    "Lesson Plan Overview", "Session Overview", "Activity Overview", "Lesson Brief",
    "Session Brief", "Learning Brief", "Teaching Brief", "Instruction Brief", "Notes for Teacher",
    "Teacher Guidance", "Student Instructions", "Student Guidance", "Lesson Notes Summary",
    "Activity Notes", "Learning Notes Summary", "Conclusion and Reflection", "Timings and Activities"
    "Conclusion", "Conclusion and Assesment"
]
    lines = [l.rstrip() for l in text.splitlines()]
    output = []
    last_header = None
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        normalised = re.sub(r'^[-•*\s]+', '', stripped)
        header_match = next((h for h in HEADER_KEYWORDS if normalised.lower().startswith(h.lower())), None)
        if header_match:
            if last_header == header_match:
                continue
            last_header = header_match
            if output and output[-1] != "":
                output.append("")
            output.append(f"@@HEADER@@{header_match}@@")
            output.append("")
            continue
        if stripped.lower().startswith("timing") or re.match(r'^\d{1,2}-\d{1,2}\s*minutes?:', stripped.lower()):
            output.append(stripped)
            output.append("")
            continue
        if stripped.startswith(("-", "•", "*")) or re.match(r'^\d+[\.\)]', stripped):
            bullet = re.sub(r'^[-•*\d\.\)\s]+', '', stripped)
            output.append(f"- {bullet}")
            continue  # tight bullets
        output.append(stripped)
        output.append("")
    final = []
    for ln in output:
        if ln == "" and final and final[-1] == "":
            continue
        final.append(ln)
    return "\n".join(final).strip()

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
            f"""<div style="display:flex; justify-content:center; align-items:center; margin-bottom:12px;">
                <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
                    <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;" />
                </div>
            </div>""",
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

import re

# -------------------------------
# Helper: HTML preview (updated)
# -------------------------------

def generate_html_preview(text: str) -> str:
    lines = text.splitlines()
    html_lines = []
    in_list = False

    # Define section titles that should always be bold
    section_titles = ["introduction", "learning objective", "evaluation", "conclusion"]

    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        # HEADER (existing @@HEADER@@ system)
        header_match = re.match(r'@@HEADER@@(.+?)@@', line)
        if header_match:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(
                f"<div style='margin-top:26px; margin-bottom:10px; font-weight:700; font-size:16px; line-height:1.3;'>{header_match.group(1)}</div>"
            )
            continue

        # BULLETS
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul style='margin-top:2px; margin-bottom:6px; padding-left:18px;'>")
                in_list = True
            html_lines.append(f"<li style='margin-bottom:2px;'>{line[2:]}</li>")
            continue

        # PARAGRAPH
        if in_list:
            html_lines.append("</ul>")
            in_list = False

        # Automatically bold section titles
        if line.lower() in section_titles:
            html_lines.append(f"<div style='margin-top:4px; margin-bottom:6px; font-weight:700;'>{line}</div>")
        else:
            html_lines.append(f"<div style='margin-top:4px; margin-bottom:6px;'>{line}</div>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)

# -------------------------------
# Generator
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message="", lesson_data=None):
    if lesson_data is None:
        lesson_data = {}
    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached. {daily_limit} lessons allowed per day.")
        return
    st.session_state.lesson_count += 1
    duration_map = {"30 min":750,"45 min":850,"60 min":1000}
    min_words = duration_map.get(lesson_data.get('lesson_duration','30 min'),750)
    st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used — {daily_limit - st.session_state.lesson_count} left")
    generation_instructions = (
    "\n\nImportant instructions for generation (must follow exactly):\n"
    "- Use British English only.\n"
    "- Do NOT include emojis.\n"
    "- Do NOT output internal lesson titles or metadata fields.\n"
    "- Start the content with the first section header.\n"
    "- Format headings as a single line header, followed by one blank line, then '-' bullet points or tight paragraph lines.\n"
    "- Collapse extra blank lines so there is at most one blank line between sections.\n"
    "- Each section must include 4–6 bullet points, each bullet written as a complete sentence with clear instructional detail.\n"
    f"- Minimum length: {min_words} words. Maximum length: 1000 words.\n"
    "- Include timings, detailed activities, differentiation, assessment, and resources.\n"
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
                    prompt_with_req += "\n\nPlease expand the lesson plan with more detail, step-by-step examples, timings, differentiation, and assessment to reach the required word count."
            if final_output is None:
                final_output = formatted or ""

            # Cleanup
            final_output = re.sub(r'(?im)^\s*(lesson\s*plan[:\-]?.*)\s*$', '', final_output)
            final_output = re.sub(r'(?im)^\s*(year\s*\d+\s*.*lesson\s*plan[:\-]?.*)\s*$', '', final_output)
            final_output = re.sub(r'(?im)(^\s*Learning\s*Objective\s*\n\s*)+', 'Learning Objective\n\n', final_output)
            final_output = re.sub(r'(?im)^\s*(Introduction\s*)\n\s*\1', r'Introduction', final_output)
            final_output = re.sub(r'\n{3,}', '\n\n', final_output).strip()
            final_output = final_output.lstrip()

            final_output_clean = re.sub(r'@@HEADER@@(.+?)@@', r'**\1**', final_output)
            final_output_html = generate_html_preview(final_output)

            # Metadata
            metadata_lines = []
            metadata_map = {
                "Lesson Title": lesson_data.get("topic",""),
                "Subject": lesson_data.get("subject",""),
                "Topic": lesson_data.get("topic",""),
                "Year Group": lesson_data.get("year_group",""),
                "Duration": lesson_data.get("lesson_duration",""),
                "Ability Level": lesson_data.get("ability_level",""),
                "SEN/EAL Notes": lesson_data.get("sen_notes",""),
                "Learning Objective": lesson_data.get("learning_objective","")
            }
            for key,value in metadata_map.items():
                if value.strip():
                    metadata_lines.append(f"<div class='metadata-line'><b>{key}:</b> {value}</div>")
            metadata_html = f"<div class='stCard'>{"".join(metadata_lines)}{final_output_html.strip()}</div>"
            st.markdown(metadata_html, unsafe_allow_html=True)

            # Exports
            pdf_buffer = create_pdf(final_output_clean)
            docx_buffer = create_docx(final_output_clean)
            st.markdown(f"""
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
""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")
            return

    # Save to history
    st.session_state.lesson_history.append({"title": title,"content": final_output})
    if regen_message:
        st.info(f"🔄 {regen_message}")

# -------------------------------
# Main page & sidebar
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
        regen_style = st.selectbox("Choose a regeneration style:", [
            "♻️ Just regenerate (different variation)",
            "🎨 More creative & engaging activities",
            "📋 More structured with timings",
            "🧩 Simplify for lower ability",
            "🚀 Challenge for higher ability"
        ])
        custom_instruction = st.text_input("Or type your own custom instruction (optional)", placeholder="e.g. Make it more interactive with outdoor activities")
        if st.button("🔁 Regenerate Lesson Plan"):
            extra_instruction = custom_instruction if custom_instruction else regen_style
            new_prompt = st.session_state.last_prompt + "\n\n" + extra_instruction
            generate_and_display_plan(new_prompt, title=f"Regenerated {len(st.session_state.lesson_history)+1}", lesson_data=lesson_data)

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
