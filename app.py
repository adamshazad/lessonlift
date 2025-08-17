import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import tempfile

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
        img {display: block; margin-left: auto; margin-right: auto;}
        .stCard {background-color: #f9f9f9 !important; color: black !important; border-radius: 12px !important; padding: 16px !important; margin-bottom: 12px !important; box-shadow: 0px 2px 5px rgba(0,0,0,0.1) !important;}
        .highlight {background-color: #fff3cd; padding: 8px; border-left: 4px solid #ffeeba; border-radius: 5px; margin-bottom: 8px;}
    </style>
""", unsafe_allow_html=True)

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
st.write("Generate **professional UK primary school lesson plans** instantly!")

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

# --- Helper: Save TXT and PDF ---
def save_lesson_file(year, subject, topic, text):
    txt_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", prefix=f"{year}_{subject}_{topic}_")
    txt_file.write(text.encode("utf-8"))
    txt_file.close()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, f"{year} {subject} - {topic}", align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    
    for line in text.split("\n"):
        if line.strip().endswith(":"):
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 8, line)
            pdf.set_font("Arial", "", 12)
        else:
            pdf.multi_cell(0, 8, line)
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix=f"{year}_{subject}_{topic}_")
    pdf.output(pdf_file.name)
    
    return txt_file, pdf_file.name

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

Format the plan for teachers:
- Bold headings for each section
- Bulleted lists for activities/resources
- SEN/EAL notes highlighted
- Clean spacing, ready to copy, print, or export
Avoid hashtags or markdown symbols.
"""
        try:
            response = model.generate_content(prompt)
            lesson_text = response.text.strip()
            txt_file, pdf_file = save_lesson_file(year_group, subject, topic, lesson_text)
            
            st.success("✅ Lesson Plan Ready!")
            
            # --- Styled Preview ---
            st.markdown("<h3>📖 Lesson Preview</h3>", unsafe_allow_html=True)
            for line in lesson_text.split("\n"):
                if line.strip().endswith(":"):
                    st.markdown(f"**{line.strip()}**")
                elif "SEN" in line or "EAL" in line:
                    st.markdown(f"<div class='highlight'>{line.strip()}</div>", unsafe_allow_html=True)
                elif line.strip():
                    st.markdown(f"- {line.strip()}")
                else:
                    st.markdown("<br>", unsafe_allow_html=True)
            
            # --- Download and Copy Buttons ---
            st.download_button("⬇ Download as TXT", data=open(txt_file.name, "r").read(), file_name="lesson_plan.txt")
            st.download_button("⬇ Download as PDF", data=open(pdf_file, "rb").read(), file_name="lesson_plan.pdf")
            
            st.text_area("📋 Copy Lesson Plan:", lesson_text, height=300)
            
        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
