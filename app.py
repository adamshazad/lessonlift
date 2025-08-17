# --- Input Form with Suggested Objectives ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    year_group = st.selectbox("Select Year Group", ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6"])
    subject = st.text_input("Subject", placeholder="e.g. Maths, English, Science")
    topic = st.text_input("Topic", placeholder="e.g. Fractions, Plants, Persuasive Writing")
    
    # Optional: auto-suggest learning objective
    learning_objective = st.text_area(
        "Learning Objective (optional)",
        placeholder="Describe what pupils should learn..."
    )
    
    suggested_obj = ""
    if subject and topic and not learning_objective.strip():
        suggested_obj = f"Understand the key concepts of {topic} in {subject} for {year_group}."
        st.info(f"Suggested Objective: *{suggested_obj}* (You can edit it if you want)")

    ability_level = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min", "45 min", "60 min"])
    sen_notes = st.text_area("SEN or EAL Notes (optional)", placeholder="Any special considerations...")

    submitted = st.form_submit_button("🚀 Generate Lesson Plan")


# --- Generate Plan with auto-filled objective if blank ---
if submitted:
    with st.spinner("✨ Creating your lesson plan..."):
        learning_objective_clean = learning_objective.strip() or suggested_obj or "Not specified"
        sen_notes_clean = sen_notes.strip() or "None"

        prompt = f"""
Create a detailed UK primary school lesson plan based on this info:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective_clean}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN or EAL Notes: {sen_notes_clean}

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
            output = getattr(response, "text", None) or getattr(response, "output_text", None) or response.candidates[0].content
            output = output.strip()

            if "plans" not in st.session_state:
                st.session_state.plans = []
            st.session_state.plans.append(output)

            st.success("✅ Lesson Plan Ready!")
            st.markdown(
                f"<div class='stCard' style='max-height:600px; overflow-y:auto'>{output.replace(chr(10), '<br>')}</div>",
                unsafe_allow_html=True
            )
            st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")
            st.download_button("⬇ Download as Markdown", data=output, file_name="lesson_plan.md")

            if len(st.session_state.plans) > 1:
                st.subheader("📜 Previously Generated Plans")
                for i, plan in enumerate(st.session_state.plans[:-1][::-1], start=1):
                    st.markdown(
                        f"<div class='stCard' style='max-height:300px; overflow-y:auto'><b>Plan #{len(st.session_state.plans)-i}</b><br>{plan.replace(chr(10), '<br>')}</div>",
                        unsafe_allow_html=True
                    )

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
