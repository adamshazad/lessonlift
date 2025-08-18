import streamlit as st
from fpdf import FPDF
import io

# Page config
st.set_page_config(page_title="LessonLift", page_icon="📚", layout="centered")

# Logo
st.image("logo.png", width=150)  # Make sure logo.png is in the same folder

st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# Lesson input
year_group = st.selectbox("Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
subject = st.text_input("Subject", "")
topic = st.text_input("Topic", "")
learning_objective = st.text_area("Learning Objective (optional)", "")
ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
lesson_duration = st.text_input("Lesson Duration (minutes)", "")
sen_notes = st.text_area("SEN/EAL Notes (optional)", "")

if st.button("Generate Lesson Plan"):
    # Generate lesson plan text
    lesson_plan = f"""
## {year_group} {subject} Lesson Plan: {topic}

**Learning Objective:** {learning_objective if learning_objective else "N/A"}
**Ability Level:** {ability_level}
**Duration:** {lesson_duration} minutes
**SEN/EAL Notes:** {sen_notes if sen_notes else "None"}

### Lesson Stages

1. **Introduction:** Starter activity and objectives.
2. **Teaching & Modelling:** Introduce and demonstrate topic.
3. **Guided Practice:** Activities to reinforce learning.
4. **Independent Practice:** Students work individually or in groups.
5. **Plenary:** Review and assess understanding.

**Differentiation:** Adapt activities for different abilities.
**Assessment:** Observe and record progress.
"""

    st.markdown(lesson_plan)

    # PDF download
    pdf_buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, f"{year_group} {subject} Lesson Plan: {topic}")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    for line in lesson_plan.splitlines():
        pdf.multi_cell(0, 8, line)
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.download_button(
        label="📥 Download Lesson Plan as PDF",
        data=pdf_buffer,
        file_name=f"{year_group}_{subject}_{topic}.pdf",
        mime="application/pdf"
    )
