import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from io import BytesIO
from textwrap import wrap
import re

st.set_page_config(page_title="LessonLift Ultimate Planner", layout="wide")
st.title("📘 LessonLift Ultimate - High-End Lesson Planner")

# --- Logo Upload ---
uploaded_logo = st.file_uploader("Upload a logo (optional)", type=["png", "jpg", "jpeg"])

# --- Number of Lessons ---
num_lessons = st.number_input("Number of Lessons", min_value=1, max_value=10, value=1)

lessons = []
for i in range(num_lessons):
    st.subheader(f"Lesson {i+1}")
    year_group = st.text_input(f"Year Group {i+1}", f"Year 1")
    subject = st.text_input(f"Subject {i+1}", "Mathematics")
    topic = st.text_input(f"Topic {i+1}", f"Lesson {i+1} Topic")
    learning_objective = st.text_area(f"Learning Objective {i+1}", "Enter learning objective here")
    ability_level = st.text_input(f"Ability Level {i+1}", "Mixed ability")
    lesson_duration = st.text_input(f"Lesson Duration {i+1}", "30 minutes")
    sen_notes = st.text_area(f"SEN/EAL Notes {i+1}", "")
    lesson_text = st.text_area(f"Lesson Plan Content {i+1}", height=200)
    
    lessons.append({
        "year_group": year_group,
        "subject": subject,
        "topic": topic,
        "learning_objective": learning_objective,
        "ability_level": ability_level,
        "lesson_duration": lesson_duration,
        "sen_notes": sen_notes,
        "lesson_text": lesson_text
    })

def format_line(text):
    """Format bullets and numbers for PDF."""
    if text.startswith("- "):
        return "• " + text[2:]
    elif re.match(r"^\d+\.\s", text):
        return text
    else:
        return text

def add_section(c, title, content, y_position, width, line_height, bg_color):
    """Add a colored header and content to PDF."""
    # Colored header
    c.setFillColor(bg_color)
    c.rect(35, y_position - 4, width - 70, line_height + 4, fill=True, stroke=False)
    # Section title
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(40, y_position, title)
    y_position -= line_height + 6

    # Wrap content
    content_lines = []
    for paragraph in content.split('\n'):
        wrapped = wrap(paragraph, 90)
        if not wrapped:
            content_lines.append("")
        else:
            for w in wrapped:
                content_lines.append(format_line(w))

    text_object = c.beginText(40, y_position)
    text_object.setFont("Helvetica", 12)
    text_object.setLeading(line_height)

    for line in content_lines:
        if y_position < 60:
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText(40, A4[1] - 40)
            text_object.setFont("Helvetica", 12)
            text_object.setLeading(line_height)
            y_position = A4[1] - 40
        if line.startswith("•"):
            text_object.setFont("Helvetica-Bold", 12)
            text_object.setFillColor(colors.darkgreen)
        text_object.textLine(line)
        text_object.setFont("Helvetica", 12)
        text_object.setFillColor(colors.black)
        y_position -= line_height
    text_object.textLine("")
    y_position -= 5
    c.drawText(text_object)
    return y_position

if st.button("Generate Ultimate Lesson PDF"):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    # --- Logo ---
    if uploaded_logo:
        logo = ImageReader(uploaded_logo)
        max_logo_width = width * 0.4
        max_logo_height = height * 0.12
        c.drawImage(logo, (width - max_logo_width)/2, height - max_logo_height - 20,
                    width=max_logo_width, height=max_logo_height, mask='auto')
        top_margin = height - max_logo_height - 40
    else:
        top_margin = height - 40

    page_number = 1
    for lesson in lessons:
        y_position = top_margin
        # Header
        c.setFont("Times-BoldItalic", 18)
        c.setFillColor(colors.darkblue)
        c.drawString(40, y_position, f"{lesson['year_group']} | {lesson['subject']} | {lesson['topic']}")
        y_position -= 30

        # Sections
        sections = [
            ("Learning Objective", lesson['learning_objective'], colors.lightblue),
            ("Ability & Duration", f"Ability Level: {lesson['ability_level']} | Duration: {lesson['lesson_duration']}", colors.lightgrey),
            ("SEN/EAL Notes", lesson['sen_notes'], colors.lightpink),
            ("Lesson Content", lesson['lesson_text'], colors.whitesmoke)
        ]

        for title, content, bg_color in sections:
            y_position = add_section(c, title, content, y_position, width, 16, bg_color)

        # Footer
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.grey)
        c.drawCentredString(width/2, 20, f"Page {page_number}")
        c.showPage()
        page_number += 1

    c.save()
    pdf_buffer.seek(0)

    st.download_button(
        label="⬇️ Download Ultimate Lesson PDF",
        data=pdf_buffer,
        file_name="Ultimate_LessonPlans.pdf",
        mime="application/pdf"
    )
