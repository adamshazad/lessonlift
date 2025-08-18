import streamlit as st
import openai
from io import BytesIO
from PIL import Image

# Set page configuration
st.set_page_config(page_title="LessonLift", page_icon="📚")

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to generate lesson plan
def generate_lesson_plan(topic):
    prompt = f"Create a clear and concise lesson plan for: {topic}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        lesson_plan = response['choices'][0]['message']['content'].strip()
        return lesson_plan
    except Exception as e:
        return f"Error generating lesson plan: {e}"

# --- Logo Section ---
st.markdown(
    """
    <div style="text-align:center;">
        <img src="logo.png" style="width:200px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); border-radius:10px;">
    </div>
    """,
    unsafe_allow_html=True
)

st.title("LessonLift: AI Lesson Plan Generator")

# --- Input Form ---
with st.form("lesson_form"):
    topic = st.text_input("Enter your lesson topic or title:")
    col1, col2 = st.columns([1,1])
    with col1:
        submit = st.form_submit_button("📄 Generate Lesson Plan")
    with col2:
        retry = st.form_submit_button("🔄 Try Again")

# --- Generate / Display Lesson Plan ---
if submit or retry:
    if not topic:
        st.warning("Please enter a lesson topic first!")
    else:
        lesson_plan = generate_lesson_plan(topic)
        # Remove extra ** or ## if they appear
        lesson_plan = lesson_plan.replace("**", "").replace("##", "")
        st.subheader("Generated Lesson Plan")
        st.text_area("Lesson Plan", lesson_plan, height=400)

        # Copy to clipboard button
        st.markdown(
            f"""
            <button onclick="navigator.clipboard.writeText(`{lesson_plan}`)">📋 Copy to Clipboard</button>
            """,
            unsafe_allow_html=True
        )
