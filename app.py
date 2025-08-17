import streamlit as st
import google.generativeai as genai
from io import BytesIO

# Try importing reportlab (for PDF export)
pdf_enabled = True
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    pdf_enabled = False

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Display Logo (centered) ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="20250721_234720958_iOS.png" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

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

Return each section as markdown starting with ### followed by content.
"""
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()

            st.success("✅ Lesson Plan Ready!")

            # --- Split sections into cards ---
            sections = output.split("### ")
            for section in sections:
                if not section.strip():
                    continue
                title, *content = section.split("\n", 1)
                body = content[0] if content else ""

                # Pick an emoji for known sections
                emoji_map = {
                    "Lesson title": "📘",
                    "Learning outcomes": "🎯",
                    "Starter activity": "🚀",
                    "Main activity": "📖",
                    "Plenary activity": "📝",
                    "Resources needed": "📦",
                    "Differentiation ideas": "🌈",
                    "Assessment methods": "✅"
                }
                emoji = emoji_map.get(title.strip().lower(), "🔹")

                # Display in card style
                st.markdown(
                    f"""
                    <div style="background-color:#f9f9f9; padding:15px; 
                                border-radius:10px; margin-bottom:15px; 
                                box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <h4>{emoji} {title.strip()}</h4>
                        <p>{body.strip().replace("\n", "<br>")}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --- Download as TXT (always available) ---
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")

            # --- Download as PDF (only if reportlab is installed) ---
            if pdf_enabled:
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer)
                styles = getSampleStyleSheet()
                story = []

                for line in output.split("\n"):
                    if line.strip().startswith("###"):
                        story.append(Paragraph(f"<b>{line.replace('###', '').strip()}</b>", styles["Heading3"]))
                    else:
                        story.append(Paragraph(line, styles["Normal"]))
                    story.append(Spacer(1, 6))

                doc.build(story)
                pdf_data = buffer.getvalue()

                st.download_button(
                    "⬇ Download as PDF",
                    data=pdf_data,
                    file_name="lesson_plan.pdf",
                    mime="application/pdf"
                )
            else:
                st.info("📄 PDF export not available (install `reportlab` to enable).")

            # --- Coming Soon Features ---
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
                st.info("🔒 Account saving is coming soon! For now, download as TXT or PDF.")

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
