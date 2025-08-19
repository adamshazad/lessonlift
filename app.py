import streamlit as st
import time

# --- Form for lesson details ---
submitted = False
try_again = False
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

    # Two buttons side by side
    colA, colB = st.columns([1,1])
    with colA:
        submitted = st.form_submit_button("🚀 Generate Lesson Plan")
    with colB:
        try_again = st.form_submit_button("🔄 Try Again")

# --- Trigger lesson generation ---
if submitted or try_again:
    # Add a visual cue for Try Again
    if try_again:
        st.info("🔄 Regenerating lesson plan, please wait...")
        time.sleep(0.5)  # tiny pause for UX effect

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

            # Display sections in cards
            sections = ["Lesson title","Learning outcomes","Starter activity","Main activity",
                        "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"]
            for sec in sections:
                start_idx = clean_output.find(sec)
                if start_idx == -1: continue
                end_idx = len(clean_output)
                for next_sec in sections:
                    if next_sec==sec: continue
                    next_idx = clean_output.find(next_sec, start_idx+1)
                    if next_idx != -1 and next_idx>start_idx:
                        end_idx = min(end_idx, next_idx)
                section_text = clean_output[start_idx:end_idx].strip()
                st.markdown(f"<div class='stCard'>{section_text}</div>", unsafe_allow_html=True)

            # Copyable text area
            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

            # Download button
            st.download_button("⬇ Download as TXT", data=clean_output, file_name="lesson_plan.txt")

        except Exception as e:
            st.error(f"Error generating lesson plan: {e}")
