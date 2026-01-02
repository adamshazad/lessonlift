# -------------------------------
# App.py - LessonLift (STABLE)
# -------------------------------

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
.stCard {
    background:#f9f9f9;
    padding:14px;
    border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.15);
    line-height:1.45;
}
.metadata-line {
    font-weight:700;
    margin-bottom:4px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Session state
# -------------------------------
if "lesson_count" not in st.session_state:
    st.session_state.lesson_count = 0
if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.date.today()

if st.session_state.last_reset != datetime.date.today():
    st.session_state.lesson_count = 0
    st.session_state.last_reset = datetime.date.today()

# -------------------------------
# OpenAI
# -------------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# -------------------------------
# Helpers
# -------------------------------
def clean_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = text.replace("•", "-")
    return text.strip()

def format_tight_output(text):
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
]

    lines = text.splitlines()
    output = []
    last_header = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        normalised = re.sub(r'^[-•*\s]+', '', line)
        header = next((h for h in HEADERS if normalised.lower().startswith(h.lower())), None)

        if header:
            if header == last_header:
                continue
            last_header = header
            output.append(f"@@HEADER@@{normalised}@@")
            output.append("")
            continue

        if line.startswith(("-", "•")):
            bullet = re.sub(r'^[-•\s]+', '', line)
            output.append(f"- {bullet}")
            continue

        output.append(line)
        output.append("")

    return "\n".join(output).strip()

# -------------------------------
# HTML generator
# -------------------------------
def generate_html(text):
    html = []
    in_list = False

    for line in text.splitlines():
        line = line.strip()

        if not line:
            if in_list:
                html.append("</ul>")
                in_list = False
            continue

        header = re.match(r'@@HEADER@@(.+?)@@', line)
        if header:
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(
                f"<div style='font-weight:700;font-size:16px;margin-top:18px;margin-bottom:6px;'>{header.group(1)}</div>"
            )
            continue

        if line.startswith("- "):
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{line[2:]}</li>")
            continue

        if in_list:
            html.append("</ul>")
            in_list = False

        html.append(f"<div>{line}</div>")

    if in_list:
        html.append("</ul>")

    return "\n".join(html)

# -------------------------------
# Exporters
# -------------------------------
def create_pdf(text):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, margin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("Normal", fontSize=11, leading=14)
    story = []

    for line in text.splitlines():
        if not line.strip():
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(line, normal))

    doc.build(story)
    buf.seek(0)
    return buf

def create_docx(text):
    doc = Document()
    for line in text.splitlines():
        header = re.match(r'@@HEADER@@(.+?)@@', line)
        if header:
            p = doc.add_paragraph()
            r = p.add_run(header.group(1))
            r.bold = True
        elif line.strip():
            doc.add_paragraph(line)
        else:
            doc.add_paragraph()
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# -------------------------------
# Generator
# -------------------------------
def generate_and_display(prompt, lesson_data):
    if st.session_state.lesson_count >= 10:
        st.error("Daily limit reached")
        return

    st.session_state.lesson_count += 1

    with st.spinner("Generating lesson..."):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3,
            max_tokens=2000
        )

    raw = response.choices[0].message.content
    cleaned = clean_markdown(raw)
    formatted = format_tight_output(cleaned)

    html = generate_html(formatted)

    metadata = []
    for k,v in lesson_data.items():
        if v:
            metadata.append(f"<div class='metadata-line'>{k}: {v}</div>")

    card = "<div class='stCard'>" + "".join(metadata) + html + "</div>"
    st.markdown(card, unsafe_allow_html=True)

    pdf = create_pdf(formatted)
    docx = create_docx(formatted)

    st.download_button("⬇ PDF", pdf, "lesson.pdf")
    st.download_button("⬇ DOCX", docx, "lesson.docx")

# -------------------------------
# UI
# -------------------------------
st.title("LessonLift")

lesson_data = {}
lesson_data["Lesson Title"] = st.text_input("Topic")
lesson_data["Subject"] = st.text_input("Subject")
lesson_data["Year Group"] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3"])
lesson_data["Duration"] = st.selectbox("Duration", ["30 min","45 min","60 min"])

if st.button("Generate"):
    prompt = f"""
Create a UK primary lesson plan.

Topic: {lesson_data["Lesson Title"]}
Subject: {lesson_data["Subject"]}
Year Group: {lesson_data["Year Group"]}
Duration: {lesson_data["Duration"]}
"""
    generate_and_display(prompt, lesson_data)
