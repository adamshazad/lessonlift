import streamlit as st
import datetime
import json
import os

# --------------------------
# Paths & Constants
# --------------------------
USER_DB_PATH = "users.json"
LOGO_PATH = "logo.png"
DAILY_LIMIT = 50

# --------------------------
# Load or Initialize Users
# --------------------------
if os.path.exists(USER_DB_PATH):
    with open(USER_DB_PATH, "r") as f:
        users = json.load(f)
else:
    users = {}

# --------------------------
# Helper Functions
# --------------------------
def save_users():
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f)

def is_valid_login(username, password):
    return username in users and users[username]["password"] == password

def register_user(username, password):
    if username in users:
        return False
    users[username] = {
        "password": password,
        "last_request_date": "",
        "daily_requests": 0
    }
    save_users()
    return True

def can_request_lesson(username):
    today = datetime.date.today().isoformat()
    if users[username]["last_request_date"] != today:
        users[username]["last_request_date"] = today
        users[username]["daily_requests"] = 0
    return users[username]["daily_requests"] < DAILY_LIMIT

def increment_requests(username):
    users[username]["daily_requests"] += 1
    save_users()

# --------------------------
# App UI
# --------------------------
st.set_page_config(page_title="LessonLift AI Lesson Planner", page_icon=LOGO_PATH)

# Display Logo and Header
st.image(LOGO_PATH, width=150)
st.title("LessonLift AI Lesson Planner")
st.subheader("Create lessons in seconds!")

# Authentication
auth_choice = st.radio("Login or Register?", ["Login", "Register"])

if auth_choice == "Register":
    new_user = st.text_input("Choose a username/email")
    new_password = st.text_input("Choose a password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_password):
            st.success("Registration successful! Please login now.")
        else:
            st.error("Username already exists. Try a different one.")

if auth_choice == "Login":
    username = st.text_input("Username/email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if is_valid_login(username, password):
            st.success(f"Welcome, {username}!")
            
            # --------------------------
            # Lesson Generator Section
            # --------------------------
            st.markdown("---")
            st.header("Generate a Lesson Plan")
            
            if can_request_lesson(username):
                subject = st.text_input("Subject (e.g., Biology, Math)")
                topic = st.text_input("Topic or Title of Lesson")
                level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
                if st.button("Generate Lesson"):
                    # Demo placeholder for lesson generator
                    st.info(f"Lesson plan generated for {topic} ({subject}) - Level: {level}")
                    increment_requests(username)
            else:
                st.warning("Maximum lessons reached for today. Come back tomorrow!")
        else:
            st.error("Invalid username or password.")