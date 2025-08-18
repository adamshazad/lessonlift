# app.py
import streamlit as st
from io import BytesIO
from fpdf import FPDF
import openai

# --- CONFIG ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", page_icon="📚", layout="centered")
st.markdown(
    """
    <style>
    .stApp { background-color: #f0f8ff; }
    .logo { width: 200px; display: block; margin-left: auto; margin-right: auto; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- LOGO ---
st.image("logo.png", use_column_width=False, width=200)  # Replace 'logo.png' with your file path

# --- HEADER ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate full UK primary school lesson plans in seconds!")

# --- USER INPUT ---
with st.form("lesson_form"):
    year = st.selectbox("Year Group", [f"Year {i}" for i in range(1, 7)])
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    duration = st.number_input("Lesson Duration (minutes)", min_value=10, max_value=120, value=30)
    ability = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    sen_notes = st.text_area("SEN/EAL Notes (optional)")
    submitted = st.form_submit_button("Generate Lesson Plan")

# --- AI GENERATION ---
if submitted:
    if not subject or not topic:
        st.warning("Please fill in both Subject and Topic fields.")
    else:
        with st.spinner("Generating lesson plan..."):
            prompt = f"""
Generate a detailed UK primary school lesson plan for {year} {subject} on the topic "{topic}".
Include: 
1. Learning Objective
2. Starter Activity
3. Teaching & Modelling (with time breakdown)
4. Guided Practice
5. Independent Practice
6. Plenary
7. Differentiation (lower and higher ability)
8. Assessment
9. Notes
Use clear, structured markdown. Include {duration} minutes lesson duration. Ability level: {ability}. SEN/EAL Notes: {sen_notes or 'None'}.
"""
            try:
                # Use your OpenAI API key
                openai.api_key = "YOUR_OPENAI_API_KEY"

                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                lesson_plan = response.choices[0].message.content

                # --- DISPLAY LESSON PLAN ---
                st.subheader("✅ Lesson Plan")
                st.markdown(lesson_plan)

                # --- DOWNLOAD TXT ---
                txt_bytes = lesson_plan.encode("utf-8")
                st.download_button("📄 Download TXT", data=txt_bytes, file_name="lesson_plan.txt", mime="text/plain")

                # --- DOWNLOAD PDF ---
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in lesson_plan.split("\n"):
                    pdf.multi_cell(0, 6, line)
                pdf_bytes = BytesIO()
                pdf.output(pdf_bytes)
                pdf_bytes.seek(0)
                st.download_button("📄 Download PDF", data=pdf_bytes, file_name="lesson_plan.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"Error generating lesson plan: {e}")
