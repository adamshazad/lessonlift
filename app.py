import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- App Config ---
st.set_page_config(page_title="LessonLift", page_icon="📚", layout="wide")

# --- Logo ---
st.image("logo.png", width=150)  # Make sure logo.png is in the same folder

st.title("📚 LessonLift - AI Lesson Planner")
st.markdown("Generate tailored UK primary school lesson plans in seconds!")

# --- Lesson Form ---
with st.form("lesson_form"):
    year_group = st.selectbox("Year Group", ["Reception", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    learning_objective = st.text_area("Learning Objective (optional)")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.text_input("Lesson Duration", "30 min")
    sen_eal_notes = st.text_area("SEN/EAL Notes (optional)")

    submitted = st.form_submit_button("Generate Lesson Plan")

if submitted:
    # --- Generate PDF ---
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, height - 50, "📚 LessonLift - AI Lesson Planner")

    pdf.setFont("Helvetica", 12)
    y = height - 100
    line_height = 18

    # Add lesson details
    details = [
        f"Year Group: {year_group}",
        f"Subject: {subject}",
        f"Topic: {topic}",
        f"Learning Objective: {learning_objective}",
        f"Ability Level: {ability_level}",
        f"Lesson Duration: {lesson_duration}",
        f"SEN/EAL Notes: {sen_eal_notes}"
    ]

    for detail in details:
        pdf.drawString(50, y, detail)
        y -= line_height

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    # --- Download Button ---
    st.download_button(
        label="📥 Download Lesson Plan as PDF",
        data=buffer,
        file_name=f"LessonPlan_{year_group}_{subject}.pdf",
        mime="application/pdf"
    )

    st.success("Lesson plan generated! Download using the button above.")
