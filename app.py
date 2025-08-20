# app.py
import re
import base64
from io import BytesIO

import streamlit as st
import google.generativeai as genai

# ---------- Optional: robust PDF (falls back gracefully if reportlab missing)
REPORTLAB_OK = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
    from reportlab.lib.units import mm
    from reportlab.lib import colors
except Exception:
    REPORTLAB_OK = False

# ---------- Page config
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# ---------- CSS (cards + green buttons)
st.markdown("""
<style>
body {background-color: white; color: black;}
.stTextInput>div>div>input, textarea, select {
  background-color: white !important; color: black !important;
  border: 1px solid #ccc !important; padding: 8px !important; border-radius: 6px !important;
}
.stCard {
  background-color: #f9f9f9 !important; color: black !important;
  border-radius: 12px !important; padding: 16px !important; margin-bottom: 12px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,.12) !important; line-height: 1.55em;
}
.download-btn {
  display: inline-block; background-color: #28a745; color: #fff !important;
  padding: 10px 18px; margin-right: 10px; border-radius: 8px; text-decoration: none;
  font-weight: 600; min-width: 160px; text-align: center; border: none;
}
.download-btn:hover { background-color: #218838; }
.download-wrap { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
.small-muted { color:#666; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar: API key
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# ---------- Logo (optional, won’t error if missing)
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
              <div style="box-shadow:0 8px 24px rgba(0,0,0,0.18); border-radius:12px; padding:8px;">
                <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;">
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

show_logo()

# ---------- Title
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# ---------- Helpers
SECTION_ALIASES = {
    "Lesson title": [r"lesson\s*title", r"title"],
    "Learning outcomes": [r"learning\s*outcomes?", r"success\s*criteria"],
    "Starter activity": [r"starter(\s*activity)?", r"hook", r"warm[-\s]*up"],
    "Main activity": [r"main(\s*activity)?", r"teaching\s*sequence", r"independent\s*task"],
    "Plenary activity": [r"plenary(\s*activity)?", r"reflection", r"review"],
    "Resources needed": [r"resources(\s*needed)?", r"materials"],
    "Differentiation ideas": [r"differentiation(\s*ideas)?", r"support\s*and\s*challenge"],
    "Assessment methods": [r"assessment(\s*methods)?", r"afl", r"formative\s*assessment"]
}

def strip_markdown(md_text: str) -> str:
    # keep content but remove formatting
    text = re.sub(r'```.*?```', '', md_text, flags=re.S)   # code fences
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)            # images
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)        # links -> text
    text = re.sub(r'#+\s*', '', text)                      # headings
    text = re.sub(r'(\*\*|\*)(.*?)\\1', r'\2', text)       # bold/italics
    text = re.sub(r'`(.*?)`', r'\1', text)                 # inline code
    return text.strip()

def find_sections(text: str):
    """Return dict of {section_title: content} using alias patterns (case-insensitive)."""
    idx_map = []
    for canonical, patterns in SECTION_ALIASES.items():
        for p in patterns:
            m = re.search(rf"(^|\n)\s*{p}\s*:?(\s*\n|-|\s)", text, flags=re.I)
            if m:
                idx_map.append((m.start(), canonical))
                break
    idx_map.sort(key=lambda x: x[0])
    if not idx_map:
        return {"Full Plan": text.strip()}
    sections = {}
    for i, (start, name) in enumerate(idx_map):
        end = idx_map[i + 1][0] if i + 1 < len(idx_map) else len(text)
        chunk = text[start:end].strip()
        # Remove the heading line itself
        chunk = re.sub(r"^[^\n]*\n?", "", chunk)
        sections[name] = chunk.strip()
    return sections

def build_pdf_from_sections(sections: dict, title: str = "Lesson Plan") -> BytesIO:
    """Pretty, wrapped, multi-page PDF using Platypus."""
    if not REPORTLAB_OK:
        return BytesIO()  # handled by caller (disable PDF button)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm
    )
    styles = getSampleStyleSheet()
    # Tweak styles
    h = ParagraphStyle(
        "Heading",
        parent=styles["Heading3"],
        spaceBefore=8, spaceAfter=6, textColor=colors.HexColor("#2f6f4e")
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        leading=14, spaceAfter=6
    )
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=colors.HexColor("#2f6f4e")
    )

    story = [Paragraph(title, title_style), Spacer(1, 6)]

    # Keep each section heading + body together where possible
    for sec, content in sections.items():
        block = [
            Paragraph(sec, h),
            Paragraph(content.replace("\n\n", "<br/><br/>").replace("\n", "<br/>"), body),
            Spacer(1, 4)
        ]
        story.append(KeepTogether(block))

    doc.build(story)
    buf.seek(0)
    return buf

def make_history_title(base_title: str, lesson_data: dict) -> str:
    yg = lesson_data.get("year_group", "").strip()
    subj = lesson_data.get("subject", "").strip()
    topic = lesson_data.get("topic", "").strip()
    parts = [p for p in [yg, subj, topic] if p]
    prefix = " – ".join(parts) if parts else "Lesson"
    return f"{prefix}: {base_title}"

# ---------- Session state
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []
if "last_prompt" not in st.session_state:
    st.session_state["last_prompt"] = ""
if "lesson_meta" not in st.session_state:
    st.session_state["lesson_meta"] = {}

# ---------- Form
with st.form("lesson_form"):
    st.subheader("Lesson Details")

    colA, colB = st.columns(2)
    with colA:
        year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        ability_level = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_duration = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    with colB:
        subject = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
        topic = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
        learning_objective = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions")

    sen_notes = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters")

    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# ---------- On submit: build prompt & generate
if submitted:
    st.session_state["lesson_meta"] = {
        "year_group": year_group,
        "ability_level": ability_level,
        "lesson_duration": lesson_duration,
        "subject": subject,
        "topic": topic,
        "learning_objective": learning_objective,
        "sen_notes": sen_notes
    }

    prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN/EAL Notes: {sen_notes or 'None'}

Format your response with clear section headings:
- Lesson title
- Learning outcomes
- Starter activity
- Main activity
- Plenary activity
- Resources needed
- Differentiation ideas
- Assessment methods
"""
    st.session_state["last_prompt"] = prompt

# ---------- Generate + render (called after submit or on regen)
def render_plan_from_prompt(prompt: str, base_title: str, regen_note: str = ""):
    with st.spinner("✨ Creating lesson plan..."):
        resp = model.generate_content(prompt)
        raw = resp.text.strip()
        clean = strip_markdown(raw)
        sections = find_sections(clean)

        # Regen note
        if regen_note:
            st.info(f"🔄 {regen_note}")

        # Cards
        for title, content in sections.items():
            st.markdown(f"<div class='stCard'><b>{title}</b><br/>{content.replace(chr(10), '<br/>')}</div>", unsafe_allow_html=True)

        # Copyable full text
        st.text_area("Full Lesson Plan (copyable)", value=clean, height=380)

        # Build PDF (if available)
        if REPORTLAB_OK:
            pdf_buf = build_pdf_from_sections(sections, title="Lesson Plan")
            pdf_b64 = base64.b64encode(pdf_buf.getvalue()).decode()
        else:
            pdf_buf, pdf_b64 = None, None

        # TXT b64
        txt_b64 = base64.b64encode(clean.encode()).decode()

        # Inline green buttons (matching shape)
        if REPORTLAB_OK:
            st.markdown(
                f"""
                <div class="download-wrap">
                  <a class="download-btn" href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt">⬇ Download as TXT</a>
                  <a class="download-btn" href="data:application/pdf;base64,{pdf_b64}" download="lesson_plan.pdf">⬇ Download as PDF</a>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="download-wrap">
                  <a class="download-btn" href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt">⬇ Download as TXT</a>
                  <span class="small-muted">PDF unavailable (install <code>reportlab</code> to enable)</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Save to history
        title = make_history_title(base_title, st.session_state.get("lesson_meta", {}))
        st.session_state["lesson_history"].append({"title": title, "content": clean})

# ---------- First generation
if submitted and st.session_state["last_prompt"]:
    render_plan_from_prompt(st.session_state["last_prompt"], base_title="Original")

# ---------- Regeneration controls
if st.session_state.get("last_prompt"):
    st.markdown("### 🔄 Not happy with the plan?")
    regen_style = st.selectbox(
        "Choose a regeneration style:",
        [
            "♻️ Just regenerate (different variation)",
            "🎨 More creative & engaging activities",
            "📋 More structured with timings",
            "🧩 Simplify for lower ability",
            "🚀 Challenge for higher ability"
        ]
    )
    custom_instruction = st.text_input(
        "Or type your own custom instruction (optional)",
        placeholder="e.g. Make the plenary a quick quiz and add outdoor learning in the main activity"
    )

    if st.button("🔁 Regenerate Lesson Plan"):
        extra, note = "", "Here’s a new updated version of your lesson plan."
        if custom_instruction.strip():
            extra = custom_instruction.strip()
            note = f"Lesson updated: {custom_instruction.strip()}"
        else:
            if regen_style == "🎨 More creative & engaging activities":
                extra, note = "Make activities more creative, interactive, and fun.", "Lesson updated with more creative and engaging activities."
            elif regen_style == "📋 More structured with timings":
                extra, note = "Add clear structure with timings for each section.", "Lesson updated with clearer structure and timings."
            elif regen_style == "🧩 Simplify for lower ability":
                extra, note = "Adapt for lower ability: simpler language, more scaffolding, step-by-step.", "Lesson simplified for lower ability."
            elif regen_style == "🚀 Challenge for higher ability":
                extra, note = "Adapt for higher ability: include stretch/challenge tasks and deeper thinking questions.", "Lesson updated with higher ability challenge tasks."
            else:
                extra = "Provide a different variation with fresh activities."

        new_prompt = st.session_state["last_prompt"] + "\n\n" + extra
        render_plan_from_prompt(new_prompt, base_title=f"Regenerated {len(st.session_state['lesson_history'])+1}", regen_note=note)

# ---------- Sidebar: History
st.sidebar.header("📚 Lesson History")
for i, lesson in enumerate(reversed(st.session_state["lesson_history"])):
    if st.sidebar.button(lesson["title"], key=f"hist_{i}"):
        st.text_area(f"Lesson History: {lesson['title']}", value=lesson["content"], height=400)