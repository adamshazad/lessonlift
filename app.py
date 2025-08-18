import streamlit as st
import google.generativeai as genai
import html
from PIL import Image

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Custom CSS ---
st.markdown("""
<style>
body {background-color: #ffffff; color: #000000; font-family: Arial, sans-serif;}
.stTextInput>div>div>input, textarea, select {
    background-color: #ffffff !important;
    color: #000 !important;
    border: 1px solid #ccc !important;
    padding: 8px !important;
    border-radius: 5px !important;
}
.stCard {
    background-color: #f9f9f9 !important;
    color: #000 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.25) !important;
    line-height: 1.6em;
    transition: transform 0.2s;
}
.stCard:hover { transform: translateY(-3px); }
.copy-btn, .print-btn {
    background-color:#4CAF50;
    color:white;
    border:none;
    padding:6px 12px;
    border-radius:5px;
    cursor:pointer;
    margin-top:5px;
    margin-right:5px;
}
.section-title {
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 6px;
}
.section-body {
    font-size: 14px;
    line-height: 1.5em;
}
img.logo {
    box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
    border-radius: 12px;
    display:block;
    margin-left:auto;
    margin-right:auto;
}
details summary {
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar API Key ---
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Logo ---
try:
    st.image("logo.png", width=200, use_column_width=False, output_format="PNG")
except FileNotFoundError:
    st.warning("Logo not found. Place 'logo.png' in the app folder.")

# --- App title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate professional UK primary school lesson plans in seconds!")

# --- Lesson Form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    learning_objective = st.text_area("Learning Objective (optional)")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
    sen_notes = st.text_area("SEN/EAL Notes (optional)")

    colA, colB = st.columns([1,1])
    submitted = colA.form_submit_button("🚀 Generate Lesson Plan")
    try_again = colB.form_submit_button("🔄 Try Again")

# --- Generate Lesson Plan ---
if submitted or try_again:
    with st.spinner("✨ Creating lesson plan..."):
        prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN/EAL Notes: {sen_notes or 'None'}
"""
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            st.success("✅ Lesson Plan Ready!")

            # --- Textarea for copy ---
            st.text_area("Lesson Plan Text", value=output, height=300, key="lesson_text")

            # --- Sections ---
            sections = ["Lesson title", "Learning outcomes", "Starter activity", 
                        "Main activity", "Plenary activity", "Resources needed", 
                        "Differentiation ideas", "Assessment methods"]
            output_lower = output.lower()

            for sec in sections:
                start_idx = output_lower.find(sec.lower())
                if start_idx == -1:
                    continue
                end_idx = len(output)
                for next_sec in sections:
                    if next_sec.lower() == sec.lower():
                        continue
                    next_idx = output_lower.find(next_sec.lower(), start_idx + 1)
                    if next_idx != -1 and next_idx > start_idx:
                        end_idx = min(end_idx, next_idx)
                section_text = output[start_idx:end_idx].strip()

                clean_text = section_text.replace("**", "").replace("##", "").replace("_", "")
                lines = clean_text.split("\n", 1)
                title = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""

                # Format activities with numbers for clarity
                if title.lower() in ["starter activity", "main activity", "plenary activity"]:
                    steps = [f"{i+1}. {s.strip().rstrip('.')}" for i, s in enumerate(body.split(". ")) if s.strip()]
                    body_html = "<br>".join(steps)
                else:
                    sentences = [s.strip() + "." for s in body.split(". ") if s.strip()]
                    body_html = "<br>".join(sentences)

                # --- Collapsible section ---
                st.markdown(f"""
                <details class='stCard'>
                    <summary class='section-title'>{title}</summary>
                    <div class='section-body'>{body_html}</div>
                </details>
                """, unsafe_allow_html=True)

            # --- Copy & Print buttons ---
            st.markdown("""
            <div>
                <button class="copy-btn" onclick="
                var text = document.querySelector('#lesson_text textarea').value;
                navigator.clipboard.writeText(text);
                alert('Lesson plan copied!');
                ">
                📋 Copy to Clipboard
                </button>
                <button class="print-btn" onclick="window.print()">
                🖨 Print Lesson Plan
                </button>
            </div>
            """, unsafe_allow_html=True)

            # --- Download button ---
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")