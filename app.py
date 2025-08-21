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
.stCard {
    background-color: #f9f9f9 !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.5em;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
api_key = None
if "gemini_api" in st.secrets:
    api_key = st.secrets["gemini_api"]

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar or configure it in st.secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Helper: strip markdown ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# --- Formatter ---
def format_lesson_text(clean_output):
    sections = [
        "Lesson title","Learning outcomes","Starter activity","Main activity",
        "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
    ]
    pattern = re.compile(r"(" + "|".join(sections) + r")[:\s]*", re.IGNORECASE)

    matches = list(pattern.finditer(clean_output))
    formatted = []
    for i, match in enumerate(matches):
        sec_name = match.group(1).title()
        start_idx = match.end()
        end_idx = matches[i+1].start() if i+1 < len(matches) else len(clean_output)
        section_text = clean_output[start_idx:end_idx].strip()
        formatted.append(f"{sec_name}\n{'-'*len(sec_name)}\n{section_text}\n")

    return "\n\n".join(formatted).strip()

# --- PDF + DOCX creators ---
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    for paragraph in text.split("\n"):
        if paragraph.strip():
            if re.match(r"^[A-Za-z ]+\n[-]+$", paragraph):  
                story.append(Paragraph(f"<b>{paragraph.splitlines()[0]}</b>", styles["Heading2"]))
            else:
                story.append(Paragraph(paragraph, styles["Normal"]))
            story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for paragraph in text.split("\n"):
        if paragraph.strip():
            if re.match(r"^[A-Za-z ]+\n[-]+$", paragraph):  
                doc.add_heading(paragraph.split("\n")[0], level=2)
            else:
                doc.add_paragraph(paragraph)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Session State ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- Main Generator ---
def generate_and_display_plan(prompt, title="Latest"):
    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)
            neat_text = format_lesson_text(clean_output)

            st.session_state["lesson_history"].append({"title": title, "content": neat_text})

            # Show preview cards
            for section in neat_text.split("\n\n"):
                if section.strip():
                    st.markdown(f"<div class='stCard'>{section}</div>", unsafe_allow_html=True)

            # Full plan textarea
            st.text_area("Full Lesson Plan (copyable)", value=neat_text, height=400)

            # --- Export downloads ---
            txt_b64 = base64.b64encode(neat_text.encode()).decode()
            pdf_bytes = create_pdf(neat_text).getvalue()
            pdf_b64 = base64.b64encode(pdf_bytes).decode()
            docx_bytes = create_docx(neat_text).getvalue()
            docx_b64 = base64.b64encode(docx_bytes).decode()

            st.markdown(
                f"""
                <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                    <a href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; background-color:#4CAF50; color:white;">⬇ TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{pdf_b64}" download="lesson_plan.pdf">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; background-color:#4CAF50; color:white;">⬇ PDF</button>
                    </a>
                    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{docx_b64}" download="lesson_plan.docx">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; background-color:#4CAF50; color:white;">⬇ DOCX</button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")

# --- Form ---
submitted = False
lesson_data = {}

with st.form("lesson_form"):
    st.subheader("Lesson Details")
    lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
    lesson_data['subject'] = st.text_input("Subject")
    lesson_data['topic'] = st.text_input("Topic")
    lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)")
    lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
    lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)")

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
