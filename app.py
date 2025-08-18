import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="LessonLift", page_icon="📚", layout="centered")

# Logo with shadow, centered
st.markdown(
    """
    <div style="text-align:center; margin-bottom:20px;">
        <img src="logo.png" style="width:150px; box-shadow: 0px 4px 8px rgba(0,0,0,0.2); border-radius:10px;">
    </div>
    """,
    unsafe_allow_html=True
)

st.title("LessonLift - Generate Lesson Plans")

# Lesson input form
with st.form("lesson_form"):
    lesson_topic = st.text_input("Enter your lesson topic or title:")
    submitted = st.form_submit_button("Generate Plan")
    try_again = st.form_submit_button("Try Again")

def generate_lesson(topic):
    prompt = f"Create a detailed, easy-to-follow lesson plan for: {topic}. Use normal sentences, no ## or ** symbols."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    lesson_text = response.choices[0].message.content
    return lesson_text

if submitted or try_again:
    if not lesson_topic.strip():
        st.warning("Please enter a lesson topic.")
    else:
        try:
            lesson_plan = generate_lesson(lesson_topic)
            st.subheader("Generated Lesson Plan")
            st.text_area("Lesson Plan", lesson_plan, height=400)

            # Copy to clipboard button
            st.markdown(
                f"""
                <button onclick="navigator.clipboard.writeText(`{lesson_plan}`)">📋 Copy to Clipboard</button>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error generating lesson plan: {str(e)}")
