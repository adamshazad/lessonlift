import streamlit as st
import google.generativeai as genai
import re
import base64

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
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Function to show logo properly ---
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

# Show logo
show_logo("logo.png", width=200)

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Helper to strip Markdown ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)           # Remove headings
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italics
    return text

# --- Form for lesson details ---
submitted = False
lesson_data = {}

with st.form("lesson_form"):
    st.subheader("Lesson Details")
    lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
    lesson_data['subject'] = st.text_input("Subject")
    lesson_data['topic'] = st.text_input("Topic")
    lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)")
    lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
    lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)")

    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# --- Generate and display lesson plan ---
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
    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            st.success("✅ Lesson Plan Ready!")

            # --- Interactive Section ---
            sections = {
                "📘 Lesson Title": "Lesson title",
                "🎯 Learning Outcomes": "Learning outcomes",
                "⚡ Starter Activity": "Starter activity",
                "🧩 Main Activity": "Main activity",
                "🔄 Plenary Activity": "Plenary activity",
                "📎 Resources Needed": "Resources needed",
                "🎚️ Differentiation Ideas": "Differentiation ideas",
                "📝 Assessment Methods": "Assessment methods"
            }

            st.subheader("📑 Interactive Lesson Plan")

            if "refinements" not in st.session_state:
                st.session_state.refinements = {}
            if "original_sections" not in st.session_state:
                st.session_state.original_sections = {}

            for emoji_title, sec in sections.items():
                start_idx = clean_output.find(sec)
                if start_idx == -1:
                    continue
                end_idx = len(clean_output)
                for next_sec in sections.values():
                    if next_sec == sec: continue
                    next_idx = clean_output.find(next_sec, start_idx+1)
                    if next_idx != -1 and next_idx > start_idx:
                        end_idx = min(end_idx, next_idx)

                section_text = clean_output[start_idx:end_idx].strip()

                if sec not in st.session_state.original_sections:
                    st.session_state.original_sections[sec] = section_text

                if sec in st.session_state.refinements:
                    section_text = st.session_state.refinements[sec]

                with st.expander(emoji_title, expanded=True if sec in ["Lesson title","Learning outcomes"] else False):
                    st.write(section_text)

                    col1, col2, col3 = st.columns(3)

                    if col1.button("✨ Enhance", key=sec+"enhance"):
                        with st.spinner(f"Enhancing {emoji_title}..."):
                            refine_prompt = f"""
                            Section: {sec}
                            Original Content:
                            {section_text}

                            Please enhance this section with more detail, engagement, and UK curriculum-appropriate language.
                            """
                            refine_response = model.generate_content(refine_prompt)
                            new_text = refine_response.text.strip()
                            st.session_state.refinements[sec] = new_text
                            st.experimental_rerun()

                    if col2.button("✂️ Simplify", key=sec+"simplify"):
                        with st.spinner(f"Simplifying {emoji_title}..."):
                            refine_prompt = f"""
                            Section: {sec}
                            Original Content:
                            {section_text}

                            Please simplify this section for easier readability and accessibility (e.g., for younger pupils or lower ability groups).
                            """
                            refine_response = model.generate_content(refine_prompt)
                            new_text = refine_response.text.strip()
                            st.session_state.refinements[sec] = new_text
                            st.experimental_rerun()

                    if col3.button("🔄 Reset", key=sec+"reset"):
                        if sec in st.session_state.refinements:
                            del st.session_state.refinements[sec]
                        st.experimental_rerun()

            # --- Final Lesson Plan (with refinements applied) ---
            final_text = clean_output
            for sec, refined_text in st.session_state.get("refinements", {}).items():
                final_text = final_text.replace(st.session_state.original_sections[sec], refined_text)

            st.text_area("Full Lesson Plan (copyable)", value=final_text, height=400)
            st.download_button("⬇ Download as TXT", data=final_text, file_name="lesson_plan.txt")

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")