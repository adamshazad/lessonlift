import streamlit as st
import os
from datetime import datetime
from fpdf import FPDF

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift", page_icon="📘", layout="centered")

# -------------------------------
# Initialize session state
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "login"
if "needs_rerun" not in st.session_state:
    st.session_state.needs_rerun = False

# -------------------------------
# Dummy user database
# -------------------------------
users_db = {
    "Adam Shazad": "password123",
    "teacher1": "teach123"
}

# -------------------------------
# Auth functions
# -------------------------------
def login_user(username, password):
    if username in users_db and users_db[username] == password:
        return True, username
    return False, "Invalid username or password"

def register_user(username, password):
    if username in users_db:
        return False, "User already exists"
    users_db[username] = password
    return True, "Registration successful! Please log in."

# -------------------------------
# PDF Generator
# -------------------------------
def save_as_pdf(title, content, filename="lesson_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, title, ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, content)
    pdf.output(filename)
    return filename

# -------------------------------
# Lesson Generator Page
# -------------------------------
def lesson_generator_page():
    # Sidebar logout button
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"
        st.session_state.needs_rerun = True
        return

    # Header
    st.image("logo.png", width=120)
    st.title("📘 LessonLift")
    st.write(f"Welcome back, **{st.session_state.username}** 👋")
    st.subheader("Generate lessons in seconds ⚡")

    # Lesson details
    year_group = st.text_input("Year Group")
    ability = st.text_input("Ability Level")
    duration = st.text_input("Lesson Duration (minutes)")
    topic = st.text_input("Topic")

    if st.button("✨ Generate Lesson Plan"):
        if not topic or not year_group or not ability or not duration:
            st.error("⚠️ Please fill in all fields.")
        else:
            with st.spinner("📝 Creating your lesson plan..."):
                # Example generated text (replace with real AI call)
                plan_text = (
                    f"Lesson Plan\n"
                    f"Year Group: {year_group}\n"
                    f"Ability Level: {ability}\n"
                    f"Lesson Duration: {duration} minutes\n"
                    f"Topic: {topic}\n\n"
                    f"Introduction:\n..."
                )

                st.success("✅ Lesson plan generated!")
                st.text_area("Lesson Plan Preview", plan_text, height=300)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "⬇️ Download as TXT",
                        data=plan_text,
                        file_name="lesson_plan.txt"
                    )
                with col2:
                    filename = save_as_pdf("Lesson Plan", plan_text)
                    with open(filename, "rb") as f:
                        st.download_button(
                            "⬇️ Download as PDF",
                            data=f,
                            file_name="lesson_plan.pdf",
                            mime="application/pdf"
                        )

# -------------------------------
# Login Page
# -------------------------------
def login_page():
    st.image("logo.png", width=150)
    st.title("📘 LessonLift")
    st.subheader("Welcome! Please log in or sign up to continue.")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab1:
        login_user_or_email = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            success, result = login_user(login_user_or_email, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = result
                st.session_state.page = "generator"
                st.session_state.needs_rerun = True
                st.success(f"Welcome back, {result}!")
            else:
                st.error(result)

    with tab2:
        new_username = st.text_input("Choose a username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up", key="signup_btn"):
            if not new_username or not new_password or not confirm_password:
                st.error("⚠️ Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                success, result = register_user(new_username, new_password)
                if success:
                    st.success(result)
                else:
                    st.error(result)

# -------------------------------
# Main Router
# -------------------------------
def main():
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "generator":
        lesson_generator_page()

    # ✅ Safe rerun trigger at end
    if st.session_state.get("needs_rerun", False):
        st.session_state.needs_rerun = False
        st.experimental_rerun()

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    main()