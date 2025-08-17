import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Display Logo ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", width=200)

# --- Force Light Mode ---
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
        padding: 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1) !important;
    }
    h2 {margin-bottom: 4px;}
    h3 {margin-bottom: 2px;}
</style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
st.sidebar.write("Enter your **Gemini API key** below.")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key.")
    st.stop()

# --- Configure Gemini ---
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate **tailored UK primary school lesson plans** in seconds.")

# --- Input Form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Select Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"], key="year_group")
    subject = st.text_input("Subject", placeholder="e.g. Maths, English, Science", key="subject")
    topic = st.text_input("Topic", placeholder="e.g. Fractions, Plants, Persuasive Writing", key="topic")
    learning_objective = st.text_area("Learning Objective (optional)", placeholder="Describe what pupils should learn...", key="learning_objective")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"], key="ability_level")
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"], key="lesson_duration")
    sen_notes = st.text_area("SEN or EAL Notes (optional)", placeholder="Any special considerations...", key="sen_notes")
    
    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- PDF Class with Header & Footer ---
class LessonPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'LessonLift - AI Lesson Planner', ln=True, align='C')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f'{st.session_state.subject} - {st.session_state.topic}', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- Function to generate plan ---
def generate_plan():
    prompt = f"""
Create a detailed UK primary school lesson plan for this info:

Year Group: {st.session_state.year_group}
Subject: {st.session_state.subject}
Topic: {st.session_state.topic}
Learning Objective: {st.session_state.learning_objective or 'Not specified'}
Ability Level: {st.session_state.ability_level}
Lesson Duration: {st.session_state.lesson_duration}
SEN or EAL Notes: {st.session_state.sen_notes or 'None'}

Provide clear headings for each section: Lesson title, Learning outcomes, Starter activity, Main activity, Plenary activity, Resources, Differentiation, Assessment.
Format for easy readability. Do not include anything unrealistic.
"""
    try:
        response = model.generate_content(prompt)
        st.session_state.last_plan = response.text.strip()
        st.success("✅ Lesson Plan Ready!")

        # Display in styled card
        st.markdown(f"<div class='stCard'>{st.session_state.last_plan.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

        # Create PDF
        pdf = LessonPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", '', 12)

        # Add Table of Contents
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, 'Table of Contents', ln=True)
        sections = ["Lesson Title", "Learning Outcomes", "Starter Activity", "Main Activity",
                    "Plenary Activity", "Resources Needed", "Differentiation Ideas", "Assessment Methods"]
        pdf.set_font("Arial", '', 12)
        for sec in sections:
            pdf.cell(0, 8, f'- {sec}', ln=True)
        pdf.ln(5)

        # Add Lesson Plan
        for line in st.session_state.last_plan.split('\n'):
            pdf.multi_cell(0, 6, line)
        pdf_output = "/tmp/lesson_plan.pdf"
        pdf.output(pdf_output)

        # Download PDF
        with open(pdf_output, "rb") as f:
            st.download_button("⬇ Download as PDF", f, file_name="lesson_plan.pdf")

    except Exception as e:
        st.error(f"Error generating lesson plan: {e}")

# --- Generate plan when submitted ---
if submitted:
    with st.spinner("✨ Creating your lesson plan..."):
        generate_plan()

# --- Try Again Button ---
if 'last_plan' in st.session_state:
    if st.button("🔄 Try Again"):
        with st.spinner("🔄 Regenerating lesson plan..."):
            generate_plan()
