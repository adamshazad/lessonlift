import streamlit as st
import re
import textwrap
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from docx import Document
import base64

# --- Session state for lesson history ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- Helper to clean markdown ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# --- PDF creator ---
def create_pdf(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin
    paragraphs = text.split("\n\n")
    for paragraph in paragraphs:
        lines = textwrap.wrap(paragraph, width=95)
        for line in lines:
            c.drawString(margin, y, line)
            y -= 14
            if y < margin:
                c.showPage()
                y = height - margin
        y -= 10
    c.save()
    buffer.seek(0)
    return buffer

# --- DOCX creator ---
def create_docx(text):
    doc = Document()
    for paragraph in text.split("\n\n"):
        doc.add_paragraph(paragraph)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Sidebar: Lesson history ---
st.sidebar.header("📚 Lesson History")
for i, lesson in enumerate(reversed(st.session_state["lesson_history"])):
    if st.sidebar.button(lesson["title"], key=f"history-{i}"):
        st.text_area(f"Lesson History: {lesson['title']}", value=lesson["content"], height=400)

# --- Page header ---
st.title("📝 Lesson Plan Generator")
st.markdown("Generate fully formatted lesson plans ready to copy or download.")

# --- User prompt input ---
prompt = st.text_area("Enter your lesson plan details or topic:", height=150)

# --- Generate button ---
if st.button("Generate Lesson Plan"):
    if prompt.strip() == "":
        st.warning("Please enter some lesson details first.")
    else:
        with st.spinner("✨ Creating lesson plan..."):
            try:
                # --- Placeholder AI response ---
                response_text = f"Year 1 Maths Lesson Plan: Shape Explorers!\nYear Group: Year 1\nSubject: Mathematics\nTopic: 2D Shapes\nLearning Objective: Pupils will be able to identify and name circles, squares, triangles, and rectangles.\nAbility Level: Mixed ability\nLesson Duration: 30 minutes\nSEN/EAL Notes: None\n\nResources:\n- Large flashcards of shapes\n- Smaller cutouts\n\nStarter Activity:\n- Quick shape identification game\n\nMain Activity:\n- Match shapes to flashcards\n\nPlenary Activity:\n- Quiz and recap\n\nDifferentiation Ideas:\n- Extra support for SEN\n- Challenge questions for advanced learners\n\nAssessment Methods:\n- Observe participation\n- Quick quiz"

                clean_output = strip_markdown(response_text)
                st.session_state["lesson_history"].append({"title": "Latest Lesson Plan", "content": clean_output})

                # --- Flexible section detection ---
                section_patterns = {
                    "Lesson Title": r"(Lesson\s*Plan|Lesson\s*Title|^.+?Lesson Plan)\:?",
                    "Learning Outcomes": r"(Learning Outcomes|Learning objective|Objective)\:?",
                    "Starter Activity": r"(Starter Activity|Starter)\:?",
                    "Main Activity": r"(Main Activity|Main)\:?",
                    "Plenary Activity": r"(Plenary Activity|Plenary)\:?",
                    "Resources Needed": r"(Resources Needed|Resources)\:?",
                    "Differentiation Ideas": r"(Differentiation Ideas|Differentiation)\:?",
                    "Assessment Methods": r"(Assessment Methods|Assessment)\:?"
                }

                # --- Split by sections to avoid blank warnings ---
                section_found = False
                for sec_name, pattern in section_patterns.items():
                    matches = list(re.finditer(pattern, clean_output, re.IGNORECASE))
                    for i, match in enumerate(matches):
                        start_idx = match.end()
                        end_idx = matches[i+1].start() if i+1 < len(matches) else len(clean_output)
                        section_text = clean_output[start_idx:end_idx].strip()
                        if section_text:
                            section_found = True
                            st.markdown(f"**{sec_name}**\n\n{section_text}")

                if not section_found:
                    st.markdown(clean_output)

                # --- Full copyable text area ---
                st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

                # --- Downloads ---
                pdf_buffer = create_pdf(clean_output)
                docx_buffer = create_docx(clean_output)
                st.markdown(
                    f"""
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download TXT</button>
                        </a>
                        <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download PDF</button>
                        </a>
                        <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
                            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download DOCX</button>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"Error generating lesson plan: {e}")
