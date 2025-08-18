import streamlit as st
from fpdf import FPDF
from io import BytesIO

# --- Brand Colors ---
HEADER_COLOR = (30, 144, 255)       # Dodger Blue
SECTION_BG_COLOR1 = (220, 235, 252)
SECTION_BG_COLOR2 = (245, 245, 245)
SECTION_LINE_COLOR = (200, 200, 200)
BULLET_COLOR = (0, 0, 0)
WATERMARK_COLOR = (200, 200, 200)

# --- App UI ---
st.set_page_config(page_title="LessonLift Ultra", page_icon="📘")
st.title("📘 LessonLift Ultra - Sale-Ready Lesson Plan Generator")

# Inputs
subject = st.text_input("Subject")
topic = st.text_input("Lesson Topic")
objectives = st.text_area("Learning Objectives (one per line)")
resources = st.text_area("Resources (one per line)")
activities = st.text_area("Activities / Teaching Steps (one per line)")
homework = st.text_area("Homework / Follow-Up Tasks (one per line)")
logo_file = st.file_uploader("Upload Your Logo (optional, PNG/JPG)", type=["png", "jpg", "jpeg"])

# Button to generate PDF
if st.button("Generate Ultra Lesson Plan PDF"):

    if not subject or not topic:
        st.error("Please provide at least Subject and Lesson Topic.")
    else:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # --- Helper Functions ---
        def add_watermark(pdf, text="LessonLift Ultra"):
            pdf.set_font("Arial", "B", 50)
            pdf.set_text_color(*WATERMARK_COLOR)
            pdf.set_xy(30, 150)
            pdf.rotate(45)
            pdf.cell(0, 0, text)
            pdf.rotate(0)

        def rotate(pdf, angle, x=None, y=None):
            if x is None: x = pdf.get_x()
            if y is None: y = pdf.get_y()
            pdf._out(f'q {angle} 0 0 {angle} {x} {y} cm')
        FPDF.rotate = rotate

        def add_section(title, content, bg_color):
            if not content.strip():
                return  # skip empty sections
            pdf.set_fill_color(*bg_color)
            pdf.set_draw_color(*SECTION_LINE_COLOR)
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 10, title, fill=True)
            pdf.ln(2)

            # Auto-resize long lines
            lines = content.split("\n")
            pdf.set_font("Arial", "", 12)
            for line in lines:
                line = line.strip()
                if line:
                    while pdf.get_string_width(line) > 180:
                        pdf.set_font("Arial", "", 10)
                        break
                    pdf.multi_cell(0, 8, f"• {line}")
            pdf.ln(3)

        # --- Add Page ---
        pdf.add_page()

        # Logo
        if logo_file:
            pdf.image(logo_file, x=80, y=10, w=50)
            pdf.ln(25)

        # Title
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(*HEADER_COLOR)
        pdf.cell(0, 12, f"{subject} - {topic}", ln=True, align="C")
        pdf.ln(5)
        pdf.set_text_color(0, 0, 0)

        # Add Sections
        add_section("Learning Objectives", objectives, SECTION_BG_COLOR1)
        add_section("Resources", resources, SECTION_BG_COLOR2)
        add_section("Activities / Teaching Steps", activities, SECTION_BG_COLOR1)
        add_section("Homework / Follow-Up Tasks", homework, SECTION_BG_COLOR2)

        # Watermark
        add_watermark(pdf)

        # Footer
        pdf.set_y(-20)
        pdf.set_font("Arial", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "LessonLift Ultra - Professional Lesson Plans", align="C")
        pdf.ln(5)
        pdf.cell(0, 5, f"Page {pdf.page_no()}", align="C")

        # Save PDF
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.success("✅ Ultra Lesson Plan PDF Generated!")
        st.download_button(
            label="Download Ultra PDF",
            data=pdf_buffer,
            file_name=f"{subject}_{topic}.pdf",
            mime="application/pdf"
        )
