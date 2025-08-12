import streamlit as st
import google.generativeai as genai

# --- Get API Key from Streamlit Secrets ---
api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.error("❌ No Gemini API key found. Please add it to Streamlit secrets.")
    st.stop()

# --- Configure Gemini ---
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- App Title ---
st.title("📚 AI Lesson Plan Generator for UK Primary Teachers")

# --- Input Form ---
with st.form("lesson_form"):
    year_group = st.selectbox("Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject (e.g. Maths, English, Science)")
    topic = st.text_input("Topic (e.g. Fractions, Plants, Persuasive Writing)")
    learning_objective = st.text_area("Learning Objective (optional)", placeholder="Describe what pupils should learn...")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
    sen_notes = st.text_area("SEN or EAL Notes (optional)", placeholder="Any special considerations...")
    
    submitted = st.form_submit_button("Generate Lesson Plan")

# --- Generate Plan ---
if submitted:
    with st.spinner("Generating lesson plan..."):
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
            st.success("✅ Lesson Plan Generated!")
            st.text_area("Lesson Plan", value=output, height=500)
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")
        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
