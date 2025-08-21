import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- CSS for styling ---
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
api_key = st.secrets.get("gemini_api", None) or st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar or configure it in st.secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Login / Signup ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "users" not in st.session_state:
    st.session_state["users"] = {}  # store username:password for this session

if not st.session_state["logged_in"]:
    st.title("🔑 LessonLift Login / Signup")
    tab = st.tabs(["Login", "Sign Up"])

    with tab[0]:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in st.session_state["users"] and st.session_state["users"][username] == password:
                st.session_state["logged_in"] = True
                st.success(f"Welcome back, {username}!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password.")

    with tab[1]:
        st.subheader("Sign Up")
        new_user = st.text_input("Choose Username", key="signup_user")
        new_pass = st.text_input("Choose Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if new_user in st.session_state["users"]:
                st.error("❌ Username already exists.")
            elif not new_user or not new_pass:
                st.error("❌ Please enter both username and password.")
            else:
                st.session_state["users"][new_user] = new_pass
                st.success(f"Account created! You can now log in as {new_user}.")

# --- Only show generator after login ---
if st.session_state["logged_in"]:

    # --- Show logo function ---
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

    # --- App title ---
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

    # --- Helper function ---
    def strip_markdown(md_text):
        text = re.sub(r'#+\s*', '', md_text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        return text

    # --- Initialize session state ---
    if "lesson_history" not in st.session_state:
        st.session_state["lesson_history"] = []

    # --- PDF generator ---
    def create_pdf(text):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=14)
        story = []
        for paragraph in text.split("\n"):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), normal_style))
                story.append(Spacer(1, 6))
        doc.build(story)
        buffer.seek(0)
        return buffer

    # --- DOCX generator ---
    def create_docx(text):
        doc = Document()
        for paragraph in text.split("\n"):
            doc.add_paragraph(paragraph.strip())
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    # --- Generate and display lesson ---
    def generate_and_display_plan(prompt, title="Latest", regen_message=""):
        with st.spinner("✨ Creating lesson plan..."):
            try:
                response = model.generate_content(prompt)
                output = response.text.strip()
                clean_output = strip_markdown(output)

                st.session_state["lesson_history"].append({"title": title, "content": clean_output})

                if regen_message:
                    st.info(f"🔄 {regen_message}")

                # Sections display
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

                st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

                # Download buttons
                pdf_buffer = create_pdf(clean_output)
                docx_buffer = create_docx(clean_output)

                st.markdown(f"""
                <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                    <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ PDF</button>
                    </a>
                    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ DOCX</button>
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
    submitted = False
    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        lesson_data['subject'] = st.selectbox("Subject", ["Maths","English","Science","History","Geography","Art","Music","PE"])
        lesson_data['topic'] = st.text_input("Lesson Topic")
        lesson_data['duration'] = st.text_input("Lesson Duration (minutes)")
        lesson_data['notes'] = st.text_area("Additional Notes / Preferences")
        submitted = st.form_submit_button("Generate Lesson Plan")

    if submitted:
        prompt_text = f"Create a {lesson_data['duration']} minute {lesson_data['subject']} lesson plan for {lesson_data['year_group']} on the topic '{lesson_data['topic']}'. Include {lesson_data['notes']}. Structure it with lesson title, learning outcomes, starter activity, main activity, plenary activity, resources needed, differentiation ideas, and assessment methods."
        generate_and_display_plan(prompt_text, title=f"{lesson_data['subject']} - {lesson_data['topic']}")

    # --- Regenerate last lesson ---
    if st.session_state["lesson_history"]:
        last_lesson = st.session_state["lesson_history"][-1]
        if st.button("🔄 Regenerate Last Lesson"):
            regenerate_prompt = f"Regenerate this lesson plan differently:\n\n{last_lesson['content']}"
            generate_and_display_plan(regenerate_prompt, title=last_lesson['title'], regen_message="Lesson regenerated!")
