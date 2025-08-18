import streamlit as st
from fpdf import FPDF
from io import BytesIO

# App title
st.set_page_config(page_title="LessonLift Ultimate", layout="centered")
st.title("LessonLift Ultimate")

# Sidebar inputs
st.sidebar.header("Lesson Plan Details")
lesson_title = st.sidebar.text_input("Lesson Title", "Sample Lesson")
subject = st.sidebar.text_input("Subject", "Sample Subject")
objectives = st.sidebar.text_area("Objectives", "List objectives here...")
activities = st.sidebar.text_area("Activities", "Describe activities...")
homework = st.sidebar.text_area("Homework", "Describe homework...")

# Logo upload or default
st.sidebar.header("Logo")
logo_file = st.sidebar.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])
use_default_logo = False
if logo_file is None:
    use_default_logo = True
    # Default logo placeholder (simple base64 or fallback text)
    default_logo_path = "logo.png"

# Generate PDF
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()

    # Add logo
    if use_default_logo:
        try:
            pdf.image(default_logo_path, x=10, y=8, w=40)
        except Exception:
            st.warning("Default logo not found, skipping logo.")
    else:
        logo_bytes = BytesIO(logo_file.read())
        pdf.image(logo_bytes, x=10, y=8, w=40)

    pdf.set_font("Arial", 'B', 16)
    pdf.ln(25)
    pdf.cell(0, 10, lesson_title, ln=True, align="C")
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, f"Subject: {subject}", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "Objectives:", ln=True)
    pdf.set_font("Arial", '', 12)
    for line in objectives.split("\n"):
        pdf.multi_cell(0, 7, line)

    pdf.ln(2)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "Activities:", ln=True)
    pdf.set_font("Arial", '', 12)
    for line in activities.split("\n"):
        pdf.multi_cell(0, 7, line)

    pdf.ln(2)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "Homework:", ln=True)
    pdf.set_font("Arial", '', 12)
    for line in homework.split("\n"):
        pdf.multi_cell(0, 7, line)

    # Watermark
    pdf.set_font("Arial", 'B', 50)
    pdf.set_text_color(200, 200, 200)
    pdf.rotate(45, x=105, y=150)
    pdf.text(20, 150, "LessonLift")
    pdf.rotate(0)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Generate TXT
def generate_txt():
    txt_content = f"Lesson Title: {lesson_title}\nSubject: {subject}\n\nObjectives:\n{objectives}\n\nActivities:\n{activities}\n\nHomework:\n{homework}"
    return txt_content

# Buttons
if st.button("Generate Lesson Plan"):
    pdf_file = generate_pdf()
    txt_file = generate_txt()

    st.success("Lesson Plan Ready!")
    st.download_button("Download PDF", pdf_file, file_name=f"{lesson_title}.pdf", mime="application/pdf")
    st.download_button("Download TXT", txt_file, file_name=f"{lesson_title}.txt", mime="text/plain")
