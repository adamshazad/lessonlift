import streamlit as st
from datetime import datetime

# Page config
st.set_page_config(page_title="LessonLift AI Lesson Planner", page_icon="logo.png")

# Logo
st.image("logo.png", width=150)

# Title and subtitle
st.title("LessonLift AI Lesson Planner")
st.subheader("Create lessons in seconds!")

# Demo mode notice
st.info("Demo mode is ON. Some features may be limited.")

# User login simulation (for demo/testing)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    with st.form("login_form"):
        st.subheader("Sign in")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Log In")

        if login_btn:
            # Demo authentication
            if username == "teacher" and password == "password":
                st.session_state['logged_in'] = True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")
else:
    st.success("You are logged in!")

    # Lesson generator form
    with st.form("lesson_form"):
        st.subheader("Generate a lesson plan")
        subject = st.text_input("Subject", placeholder="e.g., Biology")
        topic = st.text_input("Topic", placeholder="e.g., Photosynthesis")
        duration = st.selectbox("Duration", ["30 mins", "45 mins", "60 mins"])
        level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
        generate_btn = st.form_submit_button("Generate Lesson Plan")

        if generate_btn:
            # Check API quota (demo mode max 50/day)
            if 'lesson_count' not in st.session_state:
                st.session_state['lesson_count'] = 0

            if st.session_state['lesson_count'] >= 50:
                st.warning("Maximum lessons hit for today! Come back tomorrow.")
            else:
                st.session_state['lesson_count'] += 1
                # Demo generated lesson
                st.write(f"### Lesson Plan for {subject} - {topic}")
                st.write(f"Duration: {duration} | Level: {level}")
                st.write("**Learning Objectives:**")
                st.write("- Objective 1")
                st.write("- Objective 2")
                st.write("**Activities:**")
                st.write("- Activity 1")
                st.write("- Activity 2")
                st.write("**Assessment:**")
                st.write("- Assessment method")