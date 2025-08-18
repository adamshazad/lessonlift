import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from io import BytesIO
from pdf2image import convert_from_bytes
from PIL import Image

# --- CONFIG ---
st.set_page_config(
    page_title="LessonLift - Ultimate Lesson Planner",
    page_icon="📚",
    layout="wide"
)

LOGO_PATH = "logo.png"  # Make sure your logo is in the same folder
PRIMARY_COLOR = "#4B6CB7"
SECONDARY_COLOR = "#182848"

# --- HEADER ---
st.image(LOGO_PATH, width=200)
st.title("📚 LessonLift - Ultimate Lesson Planner")
st.markdown("Generate tailored UK primary school lesson plans in seconds!")

# --- FORM ---
with st.form("lesson_form"):
    col1, col2 = st.columns(2)
    with col1:
        year_group = st.selectbox("Year Group", ["Reception","Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        subject = st.selectbox("Subject", ["Math", "English", "Science", "History", "Geography", "Art", "PE"])
        topic = st.text_input("Topic")
        duration = st.number_input("Lesson Duration (minutes)", min_value=5, max_value=180, value=30)
    with col2:
        learning_obj = st.text_area("Learning Objective (optional)")
        ability = st.selectbox("Ability Level", ["Mixed", "Lower", "Higher"])
        sen_eal = st.text_area("SEN/EAL Notes (optional)")
    
    submitted = st.form_submit_button("Generate Lesson Plan")

# --- PDF GENERATION ---
def generate_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- HEADER ---
    c.setFillColor(HexColor(PRIMARY_COLOR))
    c.rect(0, height - 4*cm, width, 4*cm, fill=1)
    try:
        c.drawImage(LOGO_PATH, 2*cm, height - 3.5*cm, width=3*cm, preserveAspectRatio=True)
    except:
        pass
    c.setFillColor(HexColor("white"))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(6*cm, height - 2*cm, f"{subject} Lesson Plan")

    # --- LESSON DETAILS ---
    c.setFillColor(HexColor("black"))
    c.setFont("Helvetica", 12)
    text_y = height - 5*cm
    details = [
        f"Year Group: {year_group}",
        f"Topic: {topic}",
        f"Learning Objective: {learning_obj or 'N/A'}",
        f"Ability Level: {ability}",
        f"Lesson Duration: {duration} min",
        f"SEN/EAL Notes: {sen_eal or 'None'}"
    ]
    for detail in details:
        c.drawString(2*cm, text_y, detail)
        text_y -= 0.7*cm

    # --- SAMPLE CONTENT ---
    c.drawString(2*cm, text_y, "Lesson Structure:")
    text_y -= 0.5*cm
    content = [
        "1. Introduction",
        "2. Teaching & Modelling",
        "3. Guided Practice",
        "4. Independent Practice",
        "5. Plenary",
        "Differentiation strategies included as needed.",
    ]
    for line in content:
        c.drawString(3*cm, text_y, line)
        text_y -= 0.6*cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- ACTION ---
if submitted:
    pdf_buffer = generate_pdf()

    # --- DOWNLOAD BUTTON ---
    st.download_button(
        label="⬇️ Download Ultimate Lesson PDF",
        data=pdf_buffer,
        file_name="Ultimate_LessonPlan.pdf",
        mime="application/pdf"
    )

    # --- LIVE PREVIEW ---
    st.subheader("📄 First Page Preview")
    images = convert_from_bytes(pdf_buffer.getvalue(), first_page=1, last_page=1)
    st.image(images[0], use_container_width=True)
