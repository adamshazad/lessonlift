import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ✅ Logo at the top (auto scales)
st.image("logo.png", use_container_width=True)

st.title("📚 LessonLift - AI Lesson Planner")
st.caption("Generate tailored UK primary school lesson plans in seconds!")

# Example lesson plan (replace with your AI output)
lesson_plan = """## Year 1 Maths Lesson Plan: Shapes
...
"""

st.markdown("### ✅ Lesson Plan Ready!")
st.markdown(lesson_plan)

# ✅ Download as TXT
st.download_button(
    label="⬇️ Download Lesson Plan (TXT)",
    data=lesson_plan,
    file_name="lesson_plan.txt",
    mime="text/plain",
)

# ✅ Convert to PDF
pdf_buffer = BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=A4)
text_obj = c.beginText(50, 800)
text_obj.setFont("Helvetica", 10)

for line in lesson_plan.split("\n"):
    text_obj.textLine(line)
c.drawText(text_obj)
c.save()
pdf_buffer.seek(0)

# ✅ Download as PDF
st.download_button(
    label="⬇️ Download Lesson Plan (PDF)",
    data=pdf_buffer,
    file_name="lesson_plan.pdf",
    mime="application/pdf",
)
