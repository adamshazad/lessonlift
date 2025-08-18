import streamlit as st
import google.generativeai as genai
from PIL import Image
import html

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Custom CSS ---
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
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.5em;
}
.copy-btn {
    background-color:#4CAF50;
    color:white;
    border:none;
    padding:5px 10px;
    border-radius:5px;
    cursor:pointer;
    margin-top:5px;
}
.print-btn {
    background-color:#4CAF50;
    color:white;
    border:none;
    padding:5px 10px;
    border-radius:5px;
    cursor:pointer;
    margin-top:5px;
    margin-left:5px;
}
.stImage img {
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Logo (center + shadow) ---
try:
    logo = Image.open("logo.png")
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image(logo, width=200, use_column_width=False)
    st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.warning("⚠️ Logo not found! Make sure 'logo.png' is in the same folder as app.py")

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Form ---
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

            # Display in cards with subtitles and sentences
            sections = ["Lesson title", "Learning outcomes", "Starter activity", "Main activity", 
                        "Plenary activity", "Resources needed", "Differentiation ideas", "Assessment methods", "Homework"]
            for sec in sections:
                start_idx = output.lower().find(sec.lower())
                if start_idx == -1:
                    continue
                end_idx = len(output)
                for next_sec in sections:
                    if next_sec == sec: 
                        continue
                    next_idx = output.lower().find(next_sec.lower(), start_idx + 1)
                    if next_idx != -1 and next_idx > start_idx:
                        end_idx = min(end_idx, next_idx)
                section_text = output[start_idx:end_idx].strip()
                # Replace markdown symbols like ** or ## with clean text
                section_text = section_text.replace("**", "").replace("##", "")
                # Put each sentence on a new line
                section_text = ".\n".join([s.strip() for s in section_text.split(".") if s.strip()]) + "."
                st.markdown(f"<div class='stCard'>{section_text}</div>", unsafe_allow_html=True)

            # ✅ Copy to clipboard
            escaped_output = html.escape(output)
            st.markdown(f"""
                <button class="copy-btn" onclick="navigator.clipboard.writeText(`{escaped_output}`)">
                📋 Copy to Clipboard
                </button>
            """, unsafe_allow_html=True)

            # ✅ Print button
            st.markdown(f"""
                <button class="print-btn" onclick="var w = window.open(); w.document.write(`{escaped_output}`); w.document.close(); w.print();">
                🖨 Print Lesson Plan
                </button>
            """, unsafe_allow_html=True)

            # ✅ Download button
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")