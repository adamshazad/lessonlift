import streamlit as st
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Display Logo (centered) ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="20250721_234720958_iOS.png" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

# --- Custom Styling ---
st.markdown(
    """
    <style>
        body {background-color: white; color: black;}
        .stTextInput>div>div>input, textarea, select {
            background-color: white !important;
            color: black !important;
            border: 1px solid #ccc !important;
            padding: 8px !important;
            border-radius: 5px !important;
        }
        .lesson-card {
            background-color: #f9f9f9;
            border-left: 6px solid #2E7D32; /* green accent */
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }
        .lesson-card h3 {
            color: #1565C0; /* blue accent */
            margin-top: 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
st.sidebar.write("Enter your **Gemini API key** below to start generating lesson plans.")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()

# --- Configure Gemini ---
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Easily generate **tailored UK primary school lesson plans** in seconds. Fill in the details below and let AI do the rest!")

# --- Input Form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Select Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject", placeholder="e.g. Maths, English, Science")
    topic = st.text_input("Topic", placeholder="e.g. Fractions, Plants, Persuasive Writing")
    learning_objective = st.text_area("Learning Objective (optional)", placeholder="Describe what pupils should learn...")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
    sen_notes = st.text_area("SEN or EAL Notes (optional)", placeholder="Any special considerations...")
    
    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- Generate Plan ---
if submitted:
    with st.spinner("✨ Creating your lesson plan..."):
        prompt = f"""
Create a detailed UK primary school lesson plan based on this info:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN or EAL Notes: {sen_notes or 'None'}

Provide:
- Lesson title
- Learning outcomes
- Starter activity
- Main activity
- Plenary activity
- Resources needed
- Differentiation ideas
- Assessment methods

Format the output clearly with markdown headings (###) and bullet points.
"""

        try:
            response = model.generate_content(prompt)
            output = response.text.strip()

            st.success("✅ Lesson Plan Ready!")

            # --- Render each section inside styled cards ---
            sections = output.split("### ")
            for section in sections:
                if section.strip():
                    lines = section.split("\n", 1)
                    heading = lines[0].strip()
                    body = lines[1].strip() if len(lines) > 1 else ""
                    st.markdown(
                        f"""
                        <div class="lesson-card">
                            <h3>{heading}</h3>
                            <p>{body.replace('-', '•')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # --- Download as TXT ---
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")

            # --- Download as PDF ---
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            styles = getSampleStyleSheet()
            story = []

            for line in output.split("\n"):
                if line.strip().startswith("###"):
                    story.append(Paragraph(f"<b>{line.replace('###', '').strip()}</b>", styles["Heading3"]))
                else:
                    story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 6))

            doc.build(story)
            pdf_data = buffer.getvalue()

            st.download_button(
                "⬇ Download as PDF",
                data=pdf_data,
                file_name="lesson_plan.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
