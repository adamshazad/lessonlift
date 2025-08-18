import streamlit as st
import google.generativeai as genai

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Display Logo Centered ---
st.markdown(
    """
    <style>
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="logo-container"><img src="logo.png" width="200"></div>', unsafe_allow_html=True)

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
st.write("Easily generate **tailored UK primary school lesson plans** in seconds.")

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
    retry = st.form_submit_button("🔄 Try Again")

# --- Generate Plan ---
if submitted or retry:
    with st.spinner("✨ Creating your lesson plan..."):
        prompt = f"""
You are an expert UK primary school teacher and curriculum designer. 
Create a **detailed, professional, neatly formatted lesson plan** based on the following info:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN or EAL Notes: {sen_notes or 'None'}

Requirements:
- Use clear **headings** and **subheadings** for each section.
- Use **bullet points** where appropriate.
- Keep the content concise, structured, and easy to read.
- Include the following sections:
  1. **Lesson Title**
  2. **Learning Outcomes**
  3. **Starter Activity**
  4. **Main Activity**
  5. **Plenary Activity**
  6. **Resources Needed**
  7. **Differentiation Ideas**
  8. **Assessment Methods**
- Make sure formatting is clean: no hashtags, markdown symbols, or random characters.
- Avoid including activities the teacher may not be able to do (stick to practical, realistic classroom ideas).

Output the lesson plan ready to copy, print, or download.
"""
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            st.success("✅ Lesson Plan Ready!")

            # Display lesson plan inside a styled card
            st.markdown(f"<div class='stCard'>{output}</div>", unsafe_allow_html=True)

            # Download button (UTF-8 to avoid encoding errors)
            st.download_button("⬇ Download as TXT", data=output.encode('utf-8'), file_name="lesson_plan.txt")
        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
