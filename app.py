import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
.stDownloadButton {
    padding:10px 16px;
    font-size:14px;
    border-radius:8px;
    border:none;
    background-color:#4CAF50;
    color:white;
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

# --- Show logo ---
def show_logo(path, width=200):
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

show_logo("logo.png", width=200)

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Helper to strip Markdown ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)           # Remove headings
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italics
    return text

# --- Initialize session state ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- PDF creation with wrapped text ---
def create_pdf_wrapped(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    styleN = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        leading=16
    )
    # Split by paragraphs and maintain spacing
    paragraphs = [Paragraph(p.replace('\n', '<br/>'), styleN) for p in text.split('\n\n')]
    story = []
    for p in paragraphs:
        story.append(p)
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Function to generate and display plan ---
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
                # Robust find for section text
                pattern = re.compile(f"{sec}:(.*?)(?=({'|'.join(sections)}):|$)", re.S)
                match = pattern.search(clean_output)
                if match:
                    st.markdown(f"<div class='stCard'><b>{sec}:</b>{match.group(1).strip()}</div>", unsafe_allow_html=True)
                    # Copy to clipboard button
                    st.button(f"Copy '{sec}'", key=f"copy_{sec}", on_click=lambda text=match.group(1).strip(): st.experimental_set_query_params(text=text))

            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

            pdf_buffer = create_pdf_wrapped(clean_output)

            st.markdown(
                f"""
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                        <button class="stDownloadButton">⬇ Download TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                        <button class="stDownloadButton">⬇ Download PDF</button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")

# --- Form for lesson details ---
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
    custom_instruction = st.text_input(
        "Or type your own custom instruction (optional)",
        placeholder="e.g. Make it more interactive with outdoor activities"
    )
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
                extra_instruction = "Adapt for lower ability: simpler language, more scaffolding, step-by-step."
                regen_message = "Lesson simplified for lower ability."
            elif regen_style == "🚀 Challenge for higher ability":
                extra_instruction = "Adapt for higher ability: include stretch/challenge tasks and deeper thinking questions."
                regen_message = "Lesson updated with higher ability challenge tasks."
            else:
                regen_message = "Here’s a new updated version of your lesson plan."
        else:
            extra_instruction = custom_instruction
            regen_message = f"Lesson updated: {custom_instruction}"

        new_prompt = st.session_state["last_prompt"] + "\n\n" + extra_instruction
        generate_and_display_plan(new_prompt, title=f"Regenerated {len(st.session_state['lesson_history'])+1}", regen_message=regen_message)

# --- Sidebar: lesson history ---
st.sidebar.header("📚 Lesson History")
for i, lesson in enumerate(reversed(st.session_state["lesson_history"])):
    if st.sidebar.button(lesson["title"], key=i):
        st.text_area(f"Lesson History: {lesson['title']}", value=lesson["content"], height=400)

# --- Sidebar: Clear history ---
if st.sidebar.button("🗑 Clear Lesson History"):
    st.session_state["lesson_history"] = []
    st.experimental_rerun()