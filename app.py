# --- Display sections in interactive cards ---
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

# Store refinements and originals
if "refinements" not in st.session_state:
    st.session_state.refinements = {}
if "original_sections" not in st.session_state:
    st.session_state.original_sections = {}

for emoji_title, sec in sections.items():
    # Extract original section text
    start_idx = clean_output.find(sec)
    if start_idx == -1:
        continue
    end_idx = len(clean_output)
    for next_sec in sections.values():
        if next_sec == sec:
            continue
        next_idx = clean_output.find(next_sec, start_idx+1)
        if next_idx != -1 and next_idx > start_idx:
            end_idx = min(end_idx, next_idx)

    section_text = clean_output[start_idx:end_idx].strip()

    # Save original text for reset functionality
    if sec not in st.session_state.original_sections:
        st.session_state.original_sections[sec] = section_text

    # Use refined version if available
    if sec in st.session_state.refinements:
        section_text = st.session_state.refinements[sec]

    with st.expander(emoji_title, expanded=True if sec in ["Lesson title","Learning outcomes"] else False):
        st.write(section_text)

        col1, col2, col3 = st.columns(3)

        # --- Enhance button ---
        if col1.button(f"✨ Enhance", key=sec+"enhance"):
            with st.spinner(f"Enhancing {emoji_title}..."):
                try:
                    refine_prompt = f"""
                    Here is part of a UK primary school lesson plan:

                    Section: {sec}
                    Original Content:
                    {section_text}

                    Please enhance this section with more detail, engagement, and UK curriculum-appropriate language.
                    """
                    refine_response = model.generate_content(refine_prompt)
                    new_text = refine_response.text.strip()
                    st.session_state.refinements[sec] = new_text
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error enhancing {emoji_title}: {e}")

        # --- Simplify button ---
        if col2.button(f"✂️ Simplify", key=sec+"simplify"):
            with st.spinner(f"Simplifying {emoji_title}..."):
                try:
                    refine_prompt = f"""
                    Here is part of a UK primary school lesson plan:

                    Section: {sec}
                    Original Content:
                    {section_text}

                    Please simplify this section for easier readability and accessibility (e.g., for younger pupils or lower ability groups).
                    """
                    refine_response = model.generate_content(refine_prompt)
                    new_text = refine_response.text.strip()
                    st.session_state.refinements[sec] = new_text
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error simplifying {emoji_title}: {e}")

        # --- Reset button ---
        if col3.button(f"🔄 Reset", key=sec+"reset"):
            if sec in st.session_state.refinements:
                del st.session_state.refinements[sec]  # remove refinement
            st.experimental_rerun()