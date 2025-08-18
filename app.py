import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import date

# Page config
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# Logo display
st.image("logo.png", width=200)  # Make sure logo.png is in the same folder

st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# Lesson input form
with st.form("lesson_form"):
    year_group = st.selectbox("Year Group", [f"Year {i}" for i in range(1, 7)])
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    learning_objective = st.text_area("Learning Objective (optional)")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.text_input("Lesson Duration", value="30 minutes")
    sen_eal = st.text_area("SEN/EAL Notes (optional)")

    submitted = st.form_submit_button("Generate Lesson Plan")

if submitted:
    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Add Logo
    try:
        c.drawImage("logo.png", x=50, y=height-120, width=100, preserveAspectRatio=True, mask='auto')
    except:
        pass  # Logo missing is okay, will still generate PDF

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-150, f"{year_group} {subject} Lesson Plan")

    # Date
    c.setFont("Helvetica", 10)
    c.drawRightString(width-50, height-150, f"Date: {date.today().strftime('%d/%m/%Y')}")

    # Start Y position
    y = height - 180
    line_height = 16

    # Lesson details dictionary
    details = {
        "Year Group": year_group,
        "Subject": subject,
        "Topic": topic,
        "Learning Objective": learning_objective or "Not provided",
        "Ability Level": ability_level,
        "Lesson Duration": lesson_duration,
        "SEN/EAL Notes": sen_eal or "None",
    }

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Lesson Details:")
    y -= line_height

    c.setFont("Helvetica", 11)
    for k, v in details.items():
        for line in v.split("\n"):
            c.drawString(60, y, f"{k}: {line}")
            y -= line_height
        y -= 5  # extra spacing between fields

    # Sections of the lesson plan
    sections = [
        ("Starter Activity", "Introduce the topic with engaging activity to activate prior knowledge."),
        ("Teaching & Modelling", "Explain the key concepts and model activities with examples."),
        ("Guided Practice", "Work with students to practice the new concepts together."),
        ("Independent Practice", "Students complete tasks independently to consolidate learning."),
        ("Plenary", "Review learning objectives and assess understanding."),
        ("Differentiation", "Adjust activities to support all ability levels."),
        ("Assessment", "Observe and record student understanding and participation."),
    ]

    c.setFont("Helvetica-Bold", 12)
    for title, text in sections:
        if y < 100:  # Create new page if low
            c.showPage()
            y = height - 50
        c.drawString(50, y, f"{title}:")
        y -= line_height
        c.setFont("Helvetica", 11)
        for line in text.split("\n"):
            c.drawString(60, y, line)
            y -= line_height
        y -= 10
        c.setFont("Helvetica-Bold", 12)

    c.showPage()
    c.save()

    # Move buffer to start
    buffer.seek(0)

    st.success("✅ Lesson Plan PDF is ready!")
    st.download_button(
        label="📥 Download Lesson Plan",
        data=buffer,
        file_name=f"{year_group}_{subject}_LessonPlan.pdf",
        mime="application/pdf"
    )
