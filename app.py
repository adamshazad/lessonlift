import streamlit as st
import google.generativeai as genai
import re

# --- Custom CSS for Branding ---
st.markdown("""
    <style>
    .stApp { background-color: #f9fafc; }
    h1 { color: #2b6777; font-weight: bold; }
    h3 { color: #52ab98; }
    .stButton>button {
        background-color: #52ab98; color: white; border-radius: 8px;
        padding: 0.6em 1.2em; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #3d8b7b; color: white; }
    .stDownloadButton>button {
        background-color: #2b6777; color: white; border-radius: 8px;
        padding: 0.6em 1.2em; font-weight: bold;
    }
    .stDownloadButton>button:hover { background-color: #205259; }
    .print-button {
        background-color: #ffb703; color: black; border-radius: 8px;
        padding: 0.6em 1.2em; font-weight: bold; border: none; cursor: pointer;
    }
    .print-button:hover { background-color: #e0a106; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.image("https://via.placeholder.com/200x60.png?text=Lesson+Lift", use_container_width=True)
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()

# --- Configure Gemini ---
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- App Header ---
st.image("https://via.placeholder.com/1000x180.png?text=Lesson+Lift+-+AI+Lesson+Plans", use_container_width=True)
st.markdown("### 💡 Helping UK primary school teachers save time and inspire creativity.")

# --- Input Form ---
with st.form("lesson_form"):
    year_group = st.selectbox("Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject (e.g. Maths, English, Science)")
    topic = st.text_input("Topic (e.g. Fractions, Plants, Persuasive Writing)")
    learning_objective = st.text_area("Learning Objective (optional)", placeholder="Describe what pupils should learn...")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
    sen_notes = st.text_area("SEN or EAL Notes (optional)", placeholder="Any special considerations...")
    
    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- Generate Plan ---
if submitted:
    with st.spinner("Generating your custom lesson plan..."):
        prompt = f"""
Create a detailed UK primary school lesson plan based on this info:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN or EAL Notes: {sen_notes or 'None'}

Provide the plan in this exact format:

Lesson Title:
Learning Outcomes:
Starter Activity:
Main Activity:
Plenary Activity:
Resources Needed:
Differentiation Ideas:
Assessment Methods:
"""
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()

            # --- Split into sections ---
            sections = re.split(r"\n(?=[A-Z][a-zA-Z ]+:)", output)
            
            st.success("✅ Lesson Plan Generated!")

            # --- Display sections nicely ---
            for section in sections:
                if ":" in section:
                    title, content = section.split(":", 1)
                    st.subheader(title.strip())
                    st.write(content.strip())

            # --- Download option ---
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")

            # --- Print option ---
            st.markdown(
                f'<button class="print-button" onclick="window.print()">🖨 Print Lesson Plan</button>',
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
