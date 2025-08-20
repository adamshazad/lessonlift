import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- CSS ---
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
button {
    cursor:pointer;
}
</style>
""", unsafe_allow_html=True)

# --- Logo ---
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
            <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
                <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;">
            </div>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png' in the app folder.")

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Helper to strip Markdown ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# --- Initialize session state ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- PDF creator ---
def create_pdf_wrapped(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleN.fontSize = 12
    styleN.leading = 16
    paragraphs = [Paragraph(p.replace('\n', '<br/>'), styleN) for p in text.split('\n\n')]
    story = []
    for p in paragraphs:
        story.append(p)
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Generate & display lesson plan ---
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)
            st.session_state["lesson_history"].append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            sections = ["Lesson title","Learning outcomes","Starter activity","Main activity",
                        "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"]
            for sec in sections:
                start_idx = clean_output.find(sec)
                if start_idx == -1: 
                    continue
                end_idx = len(clean_output)
                for next_sec in sections:
                    if next_sec == sec: 
                        continue
                    next_idx = clean_output.find(next_sec, start_idx+1)
                    if next_idx != -1 and next_idx > start_idx:
                        end_idx = min(end_idx, next_idx)
                section_text = clean_output[start_idx:end_idx].strip()
                st.markdown(f"<div class='stCard'>{section_text}</div>", unsafe_allow_html=True)

            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)
            pdf_buffer = create_pdf_wrapped(clean_output)
            st.markdown(
                f"""
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                        <button style="
                            padding:10px 16px;
                            font-size:14px;
                            border-radius:8px;
                            border:none;
                            background-color:#4CAF50;
                            color:white;
                        ">⬇ Download TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                        <button style="
                            padding:10px 16px;
                            font-size:14px;
                            border-radius:8px;
                            border:none;
                            background-color:#4CAF50;
                            color:white;
                        ">⬇ Download PDF</button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")

# --- App title & logo ---
show_logo()
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Lesson form ---
submitted = False
lesson_data = {}
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
    lesson_data['subject'] = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
    lesson_data['topic'] = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
    lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions")
    lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
    lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters")
    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- Run on submit ---
if submitted:
    prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {lesson_data['year_group']}
Subject: {lesson_data['subject']}
Topic: {lesson_data['topic']}
Learning Objective: {lesson_data['learning_objective'] or 'Not specified'}
Ability Level: {lesson_data['ability_level']}
Lesson Duration: {lesson_data['lesson_duration']}
SEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}
"""
    st.session_state["last_prompt"] = prompt
    generate_and_display_plan(prompt, title="Original")

# --- Regeneration ---
if "last_prompt" in st.session_state:
    st.markdown("### 🔄 Not happy with the plan?")
    regen_style = st.selectbox(
        "Choose a regeneration style:",
        [
            "♻️ Just regenerate (different variation)",
            "🎨 More creative & engaging activities",
            "📋 More structured with timings",
            "🧩 Simplify for lower ability",
            "🚀 Challenge for higher ability"
        ]
    )
    custom_instruction = st.text_input("Or type your own custom instruction (optional)", placeholder="e.g. Make it more interactive with outdoor activities")
    if st.button("🔁 Regenerate Lesson Plan"):
        extra_instruction = ""
        regen_message = ""
        if not custom_instruction:
            if regen_style == "🎨 More creative & engaging activities":
                extra_instruction = "Make activities more creative, interactive, and fun."
                regen_message = "Lesson updated with more creative and engaging activities."
            elif regen_style == "📋 More structured with timings":
                extra_instruction = "Add clear structure with timings for each section."
                regen_message = "Lesson updated with clearer structure and timings."
            elif regen_style == "🧩 Simplify for lower ability":
                extra_instruction = "Adapt for lower ability: simpler language, more scaffolding."
                regen_message = "Lesson simplified for lower ability."
            elif regen_style == "🚀 Challenge for higher ability":
                extra_instruction = "Include extension activities and challenge tasks."
                regen_message = "Lesson enhanced for higher ability."
            else:
                extra_instruction = "Regenerate with a fresh variation."
                regen_message = "Lesson regenerated."
        else:
            extra_instruction = custom_instruction
            regen_message = f"Lesson regenerated with your custom instruction: {custom_instruction}"

        new_prompt = st.session_state["last_prompt"] + "\n\n" + extra_instruction
        generate_and_display_plan(new_prompt, title="Regenerated", regen_message=regen_message)