import streamlit as st
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from docx import Document
from docx.shared import Pt

# -------------------------------
# Authentication Helper Functions
# -------------------------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, email, password):
    users = load_users()
    if username in users or email in [u["email"] for u in users.values()]:
        return False, "Username or email already exists."
    users[username] = {"email": email, "password": password}
    save_users(users)
    return True, "Registration successful!"

def login_user(username_or_email, password):
    users = load_users()
    for username, data in users.items():
        if (username == username_or_email or data["email"] == username_or_email) and data["password"] == password:
            return True, username
    return False, "Invalid username/email or password."

# -------------------------------
# PDF Generator
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.darkblue,
        spaceBefore=12,
        spaceAfter=6
    )

    story = []
    lines = text.splitlines()
    current_list = []

    for line in lines:
        line = line.strip()
        if not line:
            if current_list:
                story.append(ListFlowable(
                    [ListItem(Paragraph(item, normal)) for item in current_list],
                    bulletType='bullet'
                ))
                current_list = []
            story.append(Spacer(1, 8))
            continue

        if any(line.lower().startswith(h) for h in [
            "lesson title", "learning outcomes", "starter activity",
            "main activity", "plenary activity", "resources needed",
            "differentiation ideas", "assessment methods"
        ]):
            if current_list:
                story.append(ListFlowable(
                    [ListItem(Paragraph(item, normal)) for item in current_list],
                    bulletType='bullet'
                ))
                current_list = []
            story.append(Paragraph(line, heading))
        elif line.startswith("-") or line[0].isdigit():
            current_list.append(line)
        else:
            story.append(Paragraph(line, normal))

    if current_list:
        story.append(ListFlowable(
            [ListItem(Paragraph(item, normal)) for item in current_list],
            bulletType='bullet'
        ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# DOCX Generator
# -------------------------------
def create_docx(text):
    doc = Document()
    lines = text.splitlines()
    for line in lines:
        if any(line.lower().startswith(h) for h in [
            "lesson title", "learning outcomes", "starter activity",
            "main activity", "plenary activity", "resources needed",
            "differentiation ideas", "assessment methods"
        ]):
            para = doc.add_paragraph(line)
            para.runs[0].font.bold = True
            para.runs[0].font.size = Pt(14)
        elif line.startswith("-") or line[0].isdigit():
            doc.add_paragraph(line, style='List Bullet')
        else:
            para = doc.add_paragraph(line)
            para.runs[0].font.size = Pt(11)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# -------------------------------
# Streamlit App Layout
# -------------------------------
st.set_page_config(page_title="📘 LessonLift AI", page_icon="📘", layout="centered")

# Centered logo
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://via.placeholder.com/200x80.png?text=LessonLift+AI" 
             style="box-shadow: 0px 4px 12px rgba(0,0,0,0.25); border-radius: 8px;"/>
        <h1>📘 LessonLift AI</h1>
        <p><em>Create lessons in seconds, powered by AI.</em></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login/Register flow
if not st.session_state.logged_in:
    choice = st.radio("🔑 Choose an option", ["Login", "Register"])

    if choice == "Login":
        login_input = st.text_input("Username or Email")
        login_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            success, msg = login_user(login_input, login_pass)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = msg
                st.success(f"Welcome back, {msg}! 🎉")
                st.experimental_rerun()
            else:
                st.error(msg)

    elif choice == "Register":
        reg_user = st.text_input("Choose a username")
        reg_email = st.text_input("Your email")
        reg_pass = st.text_input("Choose a password", type="password")
        if st.button("Register"):
            success, msg = register_user(reg_user, reg_email, reg_pass)
            if success:
                st.success(msg + " Please login now. ✅")
            else:
                st.error(msg)

else:
    st.success(f"Logged in as {st.session_state.username} 🎉")

    st.header("📝 Generate a Lesson Plan")
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    year_group = st.text_input("Year Group")
    notes = st.text_area("Additional Notes")

    if st.button("Generate Lesson Plan"):
        lesson_plan = f"""
Lesson Title: {topic}  
Learning Outcomes: - Understand the basics of {topic}.  
Starter Activity: Quick recap quiz.  
Main Activity: Group work exploring {topic}.  
Plenary Activity: Q&A session.  
Resources Needed: Worksheets, projector.  
Differentiation Ideas: Scaffolded tasks for mixed abilities.  
Assessment Methods: Exit ticket reflection.  
"""
        st.subheader("Preview")
        st.text(lesson_plan)

        pdf_buffer = create_pdf(lesson_plan)
        st.download_button("📄 Download as PDF", pdf_buffer, file_name="lesson_plan.pdf", mime="application/pdf")

        docx_buffer = create_docx(lesson_plan)
        st.download_button("📝 Download as DOCX", docx_buffer, file_name="lesson_plan.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
