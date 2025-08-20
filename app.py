import streamlit as st
from streamlit_authenticator import Authenticate
import datetime

# ----------------------------
# User authentication setup
# ----------------------------
users = {
    "usernames": {
        "teacher1": {"name": "Teacher One", "password": "hashed_password1"},
        "teacher2": {"name": "Teacher Two", "password": "hashed_password2"},
    }
}

authenticator = Authenticate(
    users,
    "lesson_lift_cookie",
    "lesson_lift_signature",
    cookie_expiry_days=30
)

# ----------------------------
# App config
# ----------------------------
st.set_page_config(page_title="LessonLift AI Planner", page_icon="📝", layout="centered")

# ----------------------------
# Session State for API usage
# ----------------------------
if "api_calls_today" not in st.session_state:
    st.session_state.api_calls_today = 0
if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.date.today()

MAX_API_CALLS = 50

# Reset daily counter
if st.session_state.last_reset != datetime.date.today():
    st.session_state.api_calls_today = 0
    st.session_state.last_reset = datetime.date.today()

# ----------------------------
# App layout
# ----------------------------
st.image("logo.png", width=200)  # replace with your logo path
st.title("LessonLift AI Lesson Planner")
st.subheader("Create lessons in seconds with AI-powered plans!")

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.success(f"Welcome {name}!")

    # API limit check
    if st.session_state.api_calls_today >= MAX_API_CALLS:
        st.warning("Maximum lesson generation limit reached for today. Please try again tomorrow.")
    else:
        st.markdown("---")
        st.header("Generate a Lesson Plan")
        subject = st.text_input("Subject", placeholder="e.g., Biology")
        topic = st.text_input("Topic", placeholder="e.g., Photosynthesis")
        grade = st.selectbox("Grade Level", ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11"])
        style = st.selectbox("Lesson Style", ["Interactive", "Lecture", "Project-Based", "Flipped Classroom"])
        generate = st.button("Generate Lesson Plan")

        if generate:
            # Increment API calls
            st.session_state.api_calls_today += 1

            # Example of generating lesson plan (replace with your actual API call)
            lesson_plan = f"**Subject:** {subject}\n\n**Topic:** {topic}\n\n**Grade:** {grade}\n\n**Style:** {style}\n\n**Lesson Plan:** This is a generated lesson plan."
            st.markdown(lesson_plan)

elif authentication_status is False:
    st.error("Invalid username or password")
elif authentication_status is None:
    st.info("Please enter your username and password to continue")

# ----------------------------
# Registration option
# ----------------------------
with st.expander("Create a new account"):
    new_user = st.text_input("Choose a username")
    new_name = st.text_input("Your full name")
    new_password = st.text_input("Choose a password", type="password")
    if st.button("Register"):
        if new_user and new_password and new_name:
            # This is a placeholder: integrate your user storage/database
            st.success(f"Account for {new_name} created! You can now log in above.")
        else:
            st.error("Please fill in all fields.")