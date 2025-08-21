import streamlit as st
import re
import textwrap
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
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
    paragraphs = text.split("\n\n")  # keep paragraph spacing
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
                # --- Here is where your AI model generates content ---
                # Replace this with your actual model call
                # Example: response = model.generate_content(prompt)
                # For demo, using placeholder text
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

                found_section = False
                for sec_name, pattern in section_patterns.items():
                    match = re.search(pattern, clean_output, re.IGNORECASE)
                    if match:
                        found_section = True
                        start_idx = match.start()
                        next_idxs = [re.search(p, clean_output[start_idx+1:], re.IGNORECASE) for p in section_patterns.values()]
                        end_idx = min([m.start()+start_idx+1 for m in next_idxs if m is not None] + [len(clean_output)])
                        section_text = clean_output[start_idx:end_idx].strip()
                        st.markdown(f"<div class='stCard'><b>{sec_name}</b><br>{section_text}</div>", unsafe_allow_html=True)

                if not found_section:
                    st.warning("⚠️ No lesson plan sections detected. Full output shown below.")
                    st.markdown(f"<div class='stCard'>{clean_output}</div>", unsafe_allow_html=True)

                # --- Full copyable text area ---
                st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

                # --- Downloads ---
                pdf_buffer = create_pdf(clean_output)
                st.markdown(
                    f"""
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download TXT</button>
                        </a>
                        <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download PDF</button>
                        </a>
                        <a href="#" id="download-docx">
                            <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download DOCX</button>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"Error generating lesson plan: {e}")
