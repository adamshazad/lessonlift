import streamlit as st
import google.generativeai as genai

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Display Logo with shadow and centered ---
st.markdown("""
    <div style="text-align:center;">
        <img src="logo.png" style="width:200px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); border-radius:12px;">
    </div>
""", unsafe_allow_html=True)

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
    try_again = st.form_submit_button("🔄 Try Again")

# --- Generate Plan ---
if submitted or try_again:
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
"""
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()

            # Remove any markdown formatting (like **)
            plain_text = output.replace("**", "")

            st.success("✅ Lesson Plan Ready!")
            st.markdown(f"<div class='stCard'>{plain_text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

            # Copy to clipboard button
            st.markdown(f"""
                <button onclick="navigator.clipboard.writeText(`{plain_text}`)" style="padding:8px 12px; margin-top:8px;">📋 Copy to Clipboard</button>
            """, unsafe_allow_html=True)

            # Download as TXT
            st.download_button("⬇ Download as TXT", data=plain_text, file_name="lesson_plan.txt")

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
