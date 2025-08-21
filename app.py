import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas  # kept from your original (we now use Platypus under the hood)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import textwrap

# DOCX is optional to avoid crashes if not installed
try:
    from docx import Document
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

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
</style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
# Keep your sidebar input, add secrets fallback (non-breaking)
api_key = st.secrets.get("gemini_api", None)
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Function to show logo (kept) ---
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

# --- App Title (kept) ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Helper to strip Markdown (kept) ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# --- Section splitter + Formatter (added for neat, consistent outputs) ---
SECTIONS_ORDER = [
    "Lesson title","Learning outcomes","Starter activity","Main activity",
    "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
]
SECTION_PATTERN = re.compile(r"(" + "|".join(SECTIONS_ORDER) + r")[:\s]*", re.IGNORECASE)

def split_sections(clean_output):
    matches = list(SECTION_PATTERN.finditer(clean_output))
    if not matches:
        return [("Lesson Plan", clean_output.strip())]

    chunks = []
    for i, m in enumerate(matches):
        name = m.group(1)
        name_norm = name.strip().title()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(clean_output)
        content = clean_output[start:end].strip()
        chunks.append((name_norm, content))
    return chunks

def format_lesson_text(clean_output):
    sections = split_sections(clean_output)
    formatted = []
    for title, body in sections:
        formatted.append(f"{title}\n{'-'*len(title)}\n{body}\n")
    return "\n\n".join(formatted).strip()

# --- Initialize session state (kept) ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- Improved PDF (uses Platypus for wrapping/headers) ---
def create_pdf(formatted_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Parse headers + paragraphs from formatted text
    lines = formatted_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line and i+1 < len(lines) and set(lines[i+1].rstrip()) == {"-"} and len(lines[i+1].rstrip()) >= len(line):
            # It's a section header
            story.append(Paragraph(f"<b>{line}</b>", styles["Heading2"]))
            story.append(Spacer(1, 6))
            i += 2  # skip underline
        else:
            if line.strip():
                story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 6))
            i += 1

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Optional DOCX (only if python-docx installed) ---
def create_docx(formatted_text):
    if not DOCX_AVAILABLE:
        return None
    doc = Document()
    lines = formatted_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line and i+1 < len(lines) and set(lines[i+1].rstrip()) == {"-"} and len(lines[i+1].rstrip()) >= len(line):
            doc.add_heading(line, level=2)
            i += 2
        else:
            if line.strip():
                doc.add_paragraph(line)
            i += 1
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Function to call Gemini and display plan (restored & enhanced formatting only) ---
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            # Build structured view + neat formatted export text
            sections = split_sections(clean_output)
            neat_text = format_lesson_text(clean_output)

            # Save to history (formatted for consistency)
            st.session_state["lesson_history"].append({"title": title, "content": neat_text})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            # Show as styled cards (restored)
            for sec_title, sec_body in sections:
                sec_html = f"<b>{sec_title}</b><br>{sec_body.replace('\n','<br>')}"
                st.markdown(f"<div class='stCard'>{sec_html}</div>", unsafe_allow_html=True)

            # Full plan (copyable) now uses neat formatted version
            st.text_area("Full Lesson Plan (copyable)", value=neat_text, height=400)

            # --- Downloads (fixed: use .getvalue() so files aren’t blank) ---
            txt_b64 = base64.b64encode(neat_text.encode()).decode()

            pdf_buf = create_pdf(neat_text)
            pdf_b64 = base64.b64encode(pdf_buf.getvalue()).decode()

            docx_b64 = None
            if DOCX_AVAILABLE:
                docx_buf = create_docx(neat_text)
                if docx_buf:
                    docx_b64 = base64.b64encode(docx_buf.getvalue()).decode()

            # Buttons (restored, now robust)
            buttons_html = f"""
                <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                    <a href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{pdf_b64}" download="lesson_plan.pdf">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download PDF</button>
                    </a>
            """
            if docx_b64:
                buttons_html += f"""
                    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{docx_b64}" download="lesson_plan.docx">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ Download DOCX</button>
                    </a>
                """
            else:
                # Subtle hint if DOCX package missing (keeps UX friendly)
                buttons_html += """
                    <span style="align-self:center; opacity:0.8;">(Install <code>python-docx</code> to enable DOCX export)</span>
                """

            buttons_html += "</div>"
            st.markdown(buttons_html, unsafe_allow_html=True)

        except Exception as e:
            msg = str(e).lower()
            if "api key" in msg:
                st.error("⚠️ Invalid or missing API key. Please check your Gemini key.")
            elif "quota" in msg:
                st.error("⚠️ API quota exceeded. Please try again later.")
            else:
                st.error(f"Error generating lesson plan: {e}")

# --- Form for lesson details (restored) ---
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

# --- Regeneration options (restored) ---
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

# --- Sidebar: lesson history (restored) ---
st.sidebar.header("📚 Lesson History")
for i, lesson in enumerate(reversed(st.session_state["lesson_history"])):
    if st.sidebar.button(lesson["title"], key=i):
        # Show as plain copyable text (like your original)
        st.text_area(f"Lesson History: {lesson['title']}", value=lesson["content"], height=400)