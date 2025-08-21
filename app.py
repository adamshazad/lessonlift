import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document

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
    line-height: 1.4em;
    font-size: 14px;
}
.stScrollable {
    max-height: 300px;
    overflow-y: auto;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #fff;
}
button {cursor:pointer;}
</style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
api_key = st.secrets.get("gemini_api", None)
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar or configure it in st.secrets.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Show logo ---
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="display:flex; justify-content:center; margin-bottom:20px;">
            <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.25);">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png'.")

show_logo()

st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Helper functions ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', md_text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    for paragraph in text.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), styles["Normal"]))
            story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for paragraph in text.split("\n"):
        doc.add_paragraph(paragraph.strip())
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Initialize session ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- Generate and display ---
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            st.session_state["lesson_history"].append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            # Sections
            sections = [
                "Lesson title","Learning outcomes","Starter activity","Main activity",
                "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
            ]
            pattern = re.compile(r"(" + "|".join(sections) + r")[:\s]*", re.IGNORECASE)
            matches = list(pattern.finditer(clean_output))
            for i, match in enumerate(matches):
                sec_name = match.group(1).capitalize()
                start_idx = match.end()
                end_idx = matches[i+1].start() if i+1 < len(matches) else len(clean_output)
                section_text = clean_output[start_idx:end_idx].strip()
                st.markdown(f"<div class='stCard'><b>{sec_name}</b><br>{section_text}</div>", unsafe_allow_html=True)

            st.markdown("<b>📌 Lesson Plan Overview</b>", unsafe_allow_html=True)
            st.markdown("<b>📝 Full Lesson Plan</b>", unsafe_allow_html=True)
            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=250)

            pdf_buffer = create_pdf(clean_output)
            docx_buffer = create_docx(clean_output)

            st.markdown(f"""
            <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                    <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white;">⬇ TXT</button>
                </a>
                <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                    <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white;">⬇ PDF</button>
                </a>
                <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
                    <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white;">⬇ DOCX</button>
                </a>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg:
                st.error("⚠️ Invalid or missing API key. Please check your Gemini key.")
            elif "quota" in error_msg:
                st.error("⚠️ API quota exceeded. Please try again later.")
            else:
                st.error(f"Error generating lesson plan: {e}")

# --- Lesson form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
    subject = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
    topic = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
    learning_objective = st.text_area("Learning Objective (optional)")
    ability_level = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    sen_notes = st.text_area("SEN/EAL Notes (optional)")

    sections_selected = st.multiselect(
        "Select sections to include:",
        [
            "Lesson title","Learning outcomes","Starter activity","Main activity",
            "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
        ],
        default=[
            "Lesson title","Learning outcomes","Starter activity","Main activity",
            "Plenary activity","Resources needed"
        ]
    )

    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

if submitted:
    section_text = ", ".join(sections_selected)
    prompt = f"""
Create a detailed UK primary school lesson plan including these sections: {section_text}

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN/EAL Notes: {sen_notes or 'None'}
"""
    st.session_state["last_prompt"] = prompt
    generate_and_display_plan(prompt, title="Original")

# --- Regeneration options ---
if "last_prompt" in st.session_state:
    st.markdown("### 🔄 Not happy with the plan?")
    regen_style = st.selectbox(
        "Choose a regeneration style:",
        [
            "♻️ Just regenerate",
            "🎨 More creative & engaging activities",
            "📋 More structured with timings",
            "🧩 Simplify for lower ability",
            "🚀 Challenge for higher ability"
        ]
    )
    custom_instruction = st.text_input("Or type your own instruction (optional)")

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
                extra_instruction = "Add challenge elements for higher ability students."
                regen_message = "Lesson updated with higher challenge."
            else:
                regen_message = "Lesson plan regenerated."
        else:
            extra_instruction = custom_instruction
            regen_message = f"Lesson regenerated with custom instruction: {custom_instruction}"

        new_prompt = st.session_state["last_prompt"] + "\n" + extra_instruction
        generate_and_display_plan(new_prompt, title="Regenerated", regen_message=regen_message)

# --- History ---
if st.session_state["lesson_history"]:
    st.sidebar.markdown("### 🕒 Lesson History")
    for i, item in enumerate(reversed(st.session_state["lesson_history"])):
        st.sidebar.markdown(f"<div class='stCard'><b>{item['title']}</b><br>{item['content'][:200]}...</div>", unsafe_allow_html=True)
