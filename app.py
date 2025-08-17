import streamlit as st
import google.generativeai as genai

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Display Logo (make sure the file is in the same GitHub repo folder as app.py) ---
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("20250721_234720958_iOS.png", width=200)  # replace with URL if needed
st.markdown("</div>", unsafe_allow_html=True)

# --- Force Light Mode + Style ---
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
        img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
st.sidebar.write("Enter your **Gemini API key** below to start generating lesson plans.")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()

# --- Configure Gemini ---
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Easily generate **tailored UK primary school lesson plans** in seconds. Fill in the details below and let AI do the rest!")

# --- Input Form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Select Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject", placeholder="e.g. Maths, English, Science")
    topic = st.text_input("Topic", placeholder="e.g. Fractions, Plants, Persuasive Writing")
    learning_objective = st.text_area("Learning Objective (optional)", placeholder="Describe what pupils should learn...")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
    sen_notes = st.text_area("SEN or EAL Notes (optional)", placeholder="Any special considerations...")

    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- Generate Plan ---
if submitted:
    with st.spinner("✨ Creating your lesson plan..."):
        prompt = f"""
Create a detailed UK primary school lesson plan based on this info:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN or EAL Notes: {sen_notes or 'None'}

Provide:
- Lesson title
- Learning outcomes
- Starter activity
- Main activity
- Plenary activity
- Resources needed
- Differentiation ideas
- Assessment methods
"""
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()

            st.success("✅ Lesson Plan Ready!")

            # --- Format into card-style sections ---
            sections = output.split("\n\n")
            for section in sections:
                if ":" in section:
                    title, body = section.split(":", 1)
                else:
                    title, body = "Section", section

                # Emoji mapping for fun
                emoji_map = {
                    "Lesson title": "📖",
                    "Learning outcomes": "🎯",
                    "Starter activity": "🚀",
                    "Main activity": "📝",
                    "Plenary activity": "🎤",
                    "Resources needed": "📦",
                    "Differentiation ideas": "🌈",
                    "Assessment methods": "✅"
                }
                emoji = emoji_map.get(title.lower().strip(), "📌")

                st.markdown(
                    f"""
                    <div style="background-color:#f0f7ff; padding:15px; 
                                border-radius:12px; margin-bottom:15px; 
                                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                                color: #222; text-align:left;">
                        <h4 style="color:#111;">{emoji} {title.strip()}</h4>
                        <p style="color:#222;">{body.strip().replace("\n", "<br>")}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --- Download buttons ---
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")

            # --- Coming Soon Banner ---
            st.markdown("---")
            st.markdown(
                """
                <div style="text-align: center; padding: 15px; 
                            background-color: #eef6ff; 
                            border-radius: 10px; margin-top: 20px;">
                    <h4>✨ Coming Soon to LessonLift</h4>
                    <p>Save all your lesson plans securely in your LessonLift account, 
                    accessible anytime, anywhere.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("💾 Save to My Account"):
                st.info("🔒 Account saving is coming soon! For now, download as TXT.")

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
