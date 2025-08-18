import streamlit as st
from openai import OpenAI

# --- Page Config ---
st.set_page_config(page_title="LessonLift", page_icon="📚", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
.stCard {
    background-color: #f9f9f9 !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.5em;
    white-space: pre-wrap;
}
button {
    margin-left: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- Logo ---
st.markdown("""
<div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px; box-shadow:0 4px 12px rgba(0,0,0,0.25); border-radius:20px; padding:10px;">
    <img src="logo.png" style="max-width:200px; height:auto; display:block; margin:0 auto;">
</div>
""", unsafe_allow_html=True)

# --- Lesson Plan Form ---
with st.form("lesson_form"):
    lesson_title = st.text_input("Lesson Title")
    year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
    subject = st.selectbox("Subject", ["Maths","English","Science","History","Geography","Other"])
    submitted = st.form_submit_button("Generate Lesson Plan")

# --- OpenAI Client ---
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

# --- Generate Lesson Plan ---
if submitted:
    try:
        prompt = f"Create a detailed lesson plan for {lesson_title} for {year_group} in {subject} without using markdown symbols like ## or **."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        lesson_plan = response.choices[0].message.content.strip()

        # --- Display Lesson Plan ---
        st.markdown(f"<div class='stCard'>{lesson_plan}</div>", unsafe_allow_html=True)

        # --- Copy to Clipboard Button ---
        st.markdown(f"""
        <button onclick="navigator.clipboard.writeText(`{lesson_plan}`)">📋 Copy to Clipboard</button>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error generating lesson plan: {e}")
