import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import datetime
import os

# ------------------------------
# CONFIGURATION
# ------------------------------
st.set_page_config(page_title="LessonLift", page_icon="📘", layout="centered")

DAILY_FREE_LIMIT = 5
DAILY_PAID_LIMIT = 10

api_keys = [
    st.secrets.get("GOOGLE_API_KEY_1"),
    st.secrets.get("GOOGLE_API_KEY_2"),
]

current_key_index = 0
api_key = api_keys[current_key_index] if api_keys else None

# ------------------------------
# MODEL INITIALIZATION FIX
# ------------------------------
model = None

if api_key:
    genai.configure(api_key=api_key)

    try:
        # List all available models
        models = genai.list_models()
        st.sidebar.write("Available models for your API key:")
        for m in models:
            st.sidebar.write(f"- {m.name}")

        # Automatically choose a working model
        preferred_models = [
            "models/gemini-2.5-pro",
            "models/gemini-2.5-flash",
            "models/gemini-2.0-pro",
            "models/gemini-pro-latest",
            "models/gemini-flash-latest"
        ]

        for mname in preferred_models:
            try:
                model = genai.GenerativeModel(mname)
                st.sidebar.success(f"✅ Using model: {mname}")
                break
            except Exception:
                continue

        if not model:
            st.sidebar.error("⚠️ Could not initialize a text model. Please check your API key access.")
    except Exception as e:
        st.sidebar.error(f"⚠️ Model listing failed: {e}")
else:
    st.sidebar.error("⚠️ No API key found. Please add your Google Gemini API key in Streamlit secrets.")


# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def format_lesson_plan(text):
    """Make lesson plan text look neat and professional."""
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(\n\d+\.)", r"<br><br>\1", text)
    text = re.sub(r"\n- ", r"<br>• ", text)
    return f"<div style='line-height:1.6; font-size:16px;'>{text}</div>"


def generate_lesson_plan(prompt):
    """Generate content using Gemini API."""
    global current_key_index

    if not model:
        st.error("⚠️ Model not initialized. Please check API setup.")
        return None

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"⚠️ Sorry, the lesson plan could not be generated at this time.\n\n{e}")
        current_key_index = (current_key_index + 1) % len(api_keys)
        return None


def create_pdf(content, title):
    """Export the plan as a PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Body", fontSize=12, leading=18))
    story = [Paragraph(title, styles["Heading1"]), Spacer(1, 12), Paragraph(content, styles["Body"])]
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def create_docx(content, title):
    """Export the plan as a Word document."""
    buffer = BytesIO()
    doc = Document()
    doc.add_heading(title, 0)
    for para in content.split("\n"):
        doc.add_paragraph(para)
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# ------------------------------
# UI & MAIN LOGIC
# ------------------------------
def lesson_generator_page():
    st.title("📘 LessonLift")
    st.caption("Generate neat, professional lesson plans powered by Gemini AI")

    st.divider()

    plan_type = st.radio("Select your access level:", ["Free Trial (5 plans/day)", "Paid (10 plans/day)"])
    daily_limit = DAILY_FREE_LIMIT if "Free" in plan_type else DAILY_PAID_LIMIT

    if "used_today" not in st.session_state:
        st.session_state.used_today = 0

    st.info(f"📅 You’ve used **{st.session_state.used_today}/{daily_limit}** plans today.")

    if st.session_state.used_today >= daily_limit:
        st.warning("🚫 You’ve reached your daily limit. Please try again tomorrow or upgrade your plan.")
        return

    topic = st.text_input("🎯 Enter your lesson topic:")
    subject = st.text_input("📚 Subject:")
    year_group = st.selectbox("🏫 Year Group:", ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11", "A-Level"])

    if st.button("✨ Generate Lesson Plan"):
        if not topic or not subject:
            st.error("⚠️ Please fill in all fields.")
            return

        st.session_state.used_today += 1
        with st.spinner("⏳ Generating your detailed lesson plan..."):
            prompt = f"Create a professional and engaging lesson plan for {subject}, topic: {topic}, aimed at {year_group} students. Include objectives, starter, activities, plenary, and homework."
            plan = generate_lesson_plan(prompt)

        if plan:
            formatted_plan = format_lesson_plan(plan)

            st.success("✅ Lesson Plan Generated Successfully!")
            st.markdown(
                f"""
                <div style='max-height:500px; overflow-y:auto; background:#f9f9f9; padding:15px;
                border-radius:10px; border:1px solid #ddd; box-shadow: 0 2px 6px rgba(0,0,0,0.05);'>
                {formatted_plan}
                </div>
                """,
                unsafe_allow_html=True,
            )

            pdf_data = create_pdf(plan, f"Lesson Plan - {topic}")
            docx_data = create_docx(plan, f"Lesson Plan - {topic}")

            st.download_button("📄 Download as PDF", data=pdf_data, file_name=f"LessonPlan_{topic}.pdf", mime="application/pdf")
            st.download_button("📝 Download as Word", data=docx_data, file_name=f"LessonPlan_{topic}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


# ------------------------------
# RUN THE APP
# ------------------------------
lesson_generator_page()
