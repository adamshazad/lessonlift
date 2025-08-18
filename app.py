import streamlit as st
import google.generativeai as genai

# --- After generating lesson plan ---
if submitted or try_again:
    with st.spinner("✨ Creating lesson plan..."):
        response = model.generate_content(prompt)
        output = response.text.strip()
        st.success("✅ Lesson Plan Ready!")

        # Display in cards
        sections = ["Lesson title", "Learning outcomes", "Starter activity", "Main activity", 
                    "Plenary activity", "Resources needed", "Differentiation ideas", "Assessment methods"]
        for sec in sections:
            start_idx = output.find(sec)
            if start_idx == -1:
                continue
            end_idx = len(output)
            for next_sec in sections:
                if next_sec == sec: 
                    continue
                next_idx = output.find(next_sec, start_idx + 1)
                if next_idx != -1 and next_idx > start_idx:
                    end_idx = min(end_idx, next_idx)
            section_text = output[start_idx:end_idx].strip()
            st.markdown(f"<div class='stCard'>{section_text}</div>", unsafe_allow_html=True)

        # --- Streamlit Copy Button ---
        st.text_area("Lesson Plan (editable / copyable)", value=output, height=400)

        # Download as TXT
        st.download_button("⬇ Download as TXT", data=output, file_name="lesson_plan.txt")
