import streamlit as st
import google.generativeai as genai

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Custom CSS ---
st.markdown("""
<style>
body {background-color: white; color: black; font-family: Arial, sans-serif;}
.stTextInput>div>div>input, textarea, select {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ccc !important;
    padding: 8px !important;
    border-radius: 5px !important;
}
.stCard {
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25) !important;
    line-height: 1.6em;
}
.stCard:nth-child(odd) { background-color: #f0f8ff !important; } /* AliceBlue */
.stCard:nth-child(even) { background-color: #fffaf0 !important; } /* FloralWhite */
.section-title {
    font-weight: bold;
    font-size: 20px;
    margin-top: 12px;
    margin-bottom: 8px;
}
.section-body {
    font-size: 15px;
    margin-left: 20px;
}
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 25px;
}
.logo-container img {
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    max-width: 220px;
    max-height: 120px;
    object-fit: contain;
}
ul {margin: 0; padding-left: 20px;}
</style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Logo ---
# Make sure logo.png is in the same folder as app.py
try:
    st.image("logo.png", use_column_width=False, width=220, caption=None)
except:
    st.warning("Logo image not found. Make sure 'logo.png' is in the same folder as app.py.")

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    learning_objective = st.text_area("Learning Objective (optional)")
    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
    sen_notes = st.text_area("SEN/EAL Notes (optional)")
    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- Generate Lesson Plan ---
if submitted:
    with st.spinner("✨ Creating lesson plan..."):
        prompt = f"""
Create a professional UK primary school lesson plan with clearly separated sections:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN/EAL Notes: {sen_notes or 'None'}

Format:
- Section titles: Lesson title, Learning outcomes, Starter activity, Main activity, Plenary activity, Resources needed, Differentiation ideas, Assessment methods
- Each section body should be concise sentences, formatted as bullet points
- Each bullet should be one complete sentence ending with a period
- No markdown symbols like ** or ##
- Make the lesson plan clean, professional, and teacher-ready
"""
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            st.success("✅ Lesson Plan Ready!")

            # --- Sections ---
            sections = ["Lesson title", "Learning outcomes", "Starter activity", 
                        "Main activity", "Plenary activity", "Resources needed", 
                        "Differentiation ideas", "Assessment methods"]
            output_lower = output.lower()

            for idx, sec in enumerate(sections):
                start_idx = output_lower.find(sec.lower())
                if start_idx == -1:
                    continue
                end_idx = len(output)
                for next_sec in sections:
                    if next_sec.lower() == sec.lower():
                        continue
                    next_idx = output_lower.find(next_sec.lower(), start_idx + 1)
                    if next_idx != -1 and next_idx > start_idx:
                        end_idx = min(end_idx, next_idx)
                section_text = output[start_idx:end_idx].strip()
                
                clean_text = section_text.replace("**", "").replace("##", "").replace("_", "")
                lines = clean_text.split("\n", 1)
                title = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
                
                bullets = [f"<li>{b.strip().rstrip('.')}.</li>" for b in body.split(". ") if b.strip()]
                bullets_html = "<ul>" + "".join(bullets) + "</ul>" if bullets else ""
                
                st.markdown(f"""
                    <div class='stCard'>
                        <div class='section-title'>{title}</div>
                        <div class='section-body'>{bullets_html}</div>
                    </div>
                """, unsafe_allow_html=True)

            # --- Full lesson plan textarea ---
            st.subheader("📋 Full Lesson Plan")
            st.text_area("Lesson Plan", value=output, height=400, key="lesson_text")

            # --- Download button ---
            st.download_button(
                label="⬇ Copy / Download Lesson Plan",
                data=output,
                file_name="lesson_plan.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")