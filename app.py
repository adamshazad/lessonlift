import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import io

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Display Logo ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", width=200)

# --- Custom CSS for Professional Look ---
st.markdown("""
    <style>
        body {background-color: #ffffff; color: #111;}
        .stTextInput>div>div>input, textarea, select {
            background-color: #ffffff !important;
            color: #111 !important;
            border: 1px solid #ccc !important;
            padding: 10px !important;
            border-radius: 8px !important;
        }
        .stCard {
            background-color: #fefefe !important;
            color: #111 !important;
            border-radius: 15px !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.12) !important;
        }
        .scroll-card {
            max-height: 650px;
            overflow-y: auto;
        }
        .stCard h1 { font-size: 1.8em; margin-bottom: 10px; }
        .stCard h2 { font-size: 1.5em; margin-top: 15px; margin-bottom: 8px; color: #222; }
        .stCard h3 { font-size: 1.3em; margin-top: 12px; margin-bottom: 6px; color: #444; }
        .stCard ul { margin-left: 20px; margin-bottom: 10px; }
        .stCard li { margin-bottom: 6px; }
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
st.write("Generate **tailored UK primary school lesson plans** in seconds.")

# --- Input Form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Select Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
    subject = st.text_input("Subject", placeholder="e.g. Maths, English, Science")
    topic = st.text_input("Topic", placeholder="e.g. Fractions, Plants, Persuasive Writing")
    learning_objective = st.text_area("Learning Objective (optional)", placeholder="Describe what pupils should learn...")
    
    suggested_obj = ""
    if subject and topic and not learning_objective.strip():
        suggested_obj = f"Understand the key concepts of {topic} in {subject} for {year_group}."
        st.info(f"Suggested Objective: *{suggested_obj}* (You can edit it)")

    ability_level = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    sen_notes = st.text_area("SEN or EAL Notes (optional)", placeholder="Any special considerations...")
    
    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- PDF Generation Function ---
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 20)
    pdf.multi_cell(0, 10, "📚 Lesson Plan", align='C')
    pdf.ln(5)

    lines = text.split("\n")
    pdf.set_font("Arial", "B", 14)
    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(2)
            continue
        if any(stripped.lower().startswith(h) for h in ["lesson title", "learning outcomes", "starter activity",
                                                        "main activity", "plenary activity", "resources needed",
                                                        "differentiation ideas", "assessment methods"]):
            pdf.set_font("Arial", "B", 14)
            pdf.multi_cell(0, 8, stripped)
            pdf.set_font("Arial", "", 12)
        elif stripped.startswith("-") or stripped.startswith("*"):
            pdf.multi_cell(0, 8, f"   • {stripped[1:].strip()}")
        else:
            pdf.multi_cell(0, 8, stripped)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# --- Generate Plan ---
if submitted:
    with st.spinner("✨ Creating your lesson plan..."):
        learning_objective_clean = learning_objective.strip() or suggested_obj or "Not specified"
        sen_notes_clean = sen_notes.strip() or "None"

        prompt = f"""
Create a detailed UK primary school lesson plan based on this info:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective_clean}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN or EAL Notes: {sen_notes_clean}

Provide:
- Lesson title
- Learning outcomes
- Starter activity
- Main activity
- Plenary activity
- Resources needed
- Differentiation ideas
- Assessment methods
"""
        try:
            response = model.generate_content(prompt)
            output = getattr(response, "text", None) or getattr(response, "output_text", None) or response.candidates[0].content
            output = output.strip()

            if "plans" not in st.session_state:
                st.session_state.plans = []
            st.session_state.plans.append(output)

            st.success("✅ Lesson Plan Ready!")

            # Display plan
            st.markdown(f"<div class='stCard scroll-card'>{output}</div>", unsafe_allow_html=True)

            # Downloads
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")
            st.download_button("⬇ Download as Markdown", data=output, file_name="lesson_plan.md")
            pdf_file = generate_pdf(output)
            st.download_button("⬇ Download as PDF", data=pdf_file, file_name="lesson_plan.pdf", mime="application/pdf")

            # Previous plans
            if len(st.session_state.plans) > 1:
                st.subheader("📜 Previously Generated Plans")
                for i, plan in enumerate(st.session_state.plans[:-1][::-1], start=1):
                    st.markdown(
                        f"<div class='stCard scroll-card' style='max-height:300px; padding:12px'><b>Plan #{len(st.session_state.plans)-i}</b></div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(plan)

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
