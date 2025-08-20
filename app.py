import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- CSS ---
st.markdown("""
<style>
body {background-color: white; color: black;}
.stTextInput>div>div>input, textarea, select {background-color:white !important;color:black !important;border:1px solid #ccc !important;padding:8px !important;border-radius:5px !important;}
.stCard {background-color:#f9f9f9 !important;color:black !important;border-radius:12px !important;padding:16px !important;margin-bottom:12px !important;box-shadow:0px 2px 8px rgba(0,0,0,0.15) !important;line-height:1.5em;}
button{cursor:pointer;}
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

# --- Logo ---
def show_logo(path, width=200):
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"<div style='display:flex; justify-content:center; margin-bottom:20px;'><div style='box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;'><img src='data:image/png;base64,{b64}' width='{width}' style='border-radius:12px;'></div></div>", unsafe_allow_html=True)
    except: st.warning("Logo file not found. Please upload 'logo.png' in the app folder.")
show_logo("logo.png", width=200)

# --- App Title ---
st.title("📚 LessonLift - AI Lesson Planner")
st.write("Generate tailored UK primary school lesson plans in seconds!")

# --- Helpers ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,rightMargin=40,leftMargin=40,topMargin=50,bottomMargin=50)
    style = getSampleStyleSheet()["Normal"]
    style.fontSize, style.leading = 12, 16
    story = [Paragraph(p.replace("\n","<br/>"), style) for p in text.split("\n\n")]
    interleaved = []
    for p in story:
        interleaved.append(p)
        interleaved.append(Spacer(1,12))
    doc.build(interleaved)
    buffer.seek(0)
    return buffer

# --- Session State ---
if "lesson_history" not in st.session_state: st.session_state["lesson_history"] = []
if "clear_history" not in st.session_state: st.session_state.clear_history = False

# --- Generate & display ---
def generate_plan(prompt, title="Latest", regen_message=""):
    with st.spinner("✨ Creating lesson plan..."):
        try:
            output = strip_markdown(model.generate_content(prompt).text.strip())
            st.session_state["lesson_history"].append({"title": title, "content": output})

            if regen_message: st.info(f"🔄 {regen_message}")

            sections = ["Lesson title","Learning outcomes","Starter activity","Main activity","Plenary activity","Resources needed","Differentiation ideas","Assessment methods"]
            for sec in sections:
                start_idx = output.find(sec)
                if start_idx==-1: continue
                end_idx = len(output)
                for nxt in sections:
                    if nxt==sec: continue
                    nxt_idx = output.find(nxt, start_idx+1)
                    if nxt_idx!=-1 and nxt_idx>start_idx: end_idx=min(end_idx,nxt_idx)
                st.markdown(f"<div class='stCard'>{output[start_idx:end_idx].strip()}</div>", unsafe_allow_html=True)

            st.text_area("Full Lesson Plan (copyable)", value=output, height=400)
            pdf_buf = create_pdf(output)

            txt_b64 = base64.b64encode(output.encode()).decode()
            pdf_b64 = base64.b64encode(pdf_buf.read()).decode()
            st.markdown(f"""<div style="display:flex; gap:10px; margin-top:10px;">
                <a href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt"><button style="padding:10px 16px;font-size:14px;border-radius:8px;border:none;background-color:#4CAF50;color:white;">⬇ Download TXT</button></a>
                <a href="data:application/pdf;base64,{pdf_b64}" download="lesson_plan.pdf"><button style="padding:10px 16px;font-size:14px;border-radius:8px;border:none;background-color:#4CAF50;color:white;">⬇ Download PDF</button></a>
                </div>""", unsafe_allow_html=True)

        except Exception as e: st.error(f"Error generating lesson plan: {e}")

# --- Lesson form ---
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    lesson_data = {
        'year_group': st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"]),
        'subject': st.text_input("Subject", placeholder="e.g. English, Maths, Science"),
        'topic': st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth"),
        'learning_objective': st.text_area("Learning Objective (optional)"),
        'ability_level': st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"]),
        'lesson_duration': st.selectbox("Lesson Duration", ["30 min","45 min","60 min"]),
        'sen_notes': st.text_area("SEN/EAL Notes (optional)")
    }
    if st.form_submit_button("🚀 Generate Lesson Plan"):
        prompt = f"""Create a detailed UK primary school lesson plan:
Year Group: {lesson_data['year_group']}
Subject: {lesson_data['subject']}
Topic: {lesson_data['topic']}
Learning Objective: {lesson_data['learning_objective'] or 'Not specified'}
Ability Level: {lesson_data['ability_level']}
Lesson Duration: {lesson_data['lesson_duration']}
SEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}"""
        st.session_state["last_prompt"] = prompt
        generate_plan(prompt, title="Original")

# --- Regeneration ---
if "last_prompt" in st.session_state:
    st.markdown("### 🔄 Not happy with the plan?")
    regen_style = st.selectbox("Choose regeneration style:", ["♻️ Just regenerate","🎨 More creative","📋 Structured with timings","🧩 Simplify for lower ability","🚀 Challenge for higher ability"])
    custom_instruction = st.text_input("Or type custom instruction (optional)")
    if st.button("Regenerate Lesson Plan"):
        regen_prompt = st.session_state["last_prompt"]
        if custom_instruction: regen_prompt += f"\n\nAdditional instruction: {custom_instruction}"
        else: regen_prompt += f"\n\nRegeneration style: {regen_style}"
        generate_plan(regen_prompt, title="Regenerated", regen_message="Regenerated lesson plan applied!")

# --- Sidebar: History ---
st.sidebar.subheader("📜 Lesson History")
if st.session_state["lesson_history"]:
    for entry in reversed(st.session_state["lesson_history"]): st.sidebar.markdown(f"**{entry['title']}**")
else: st.sidebar.info("No lesson history yet.")

# --- Sidebar: Clear history ---
if st.sidebar.button("🗑 Clear Lesson History"):
    st.session_state["lesson_history"]=[]
    st.session_state.clear_history=True
if st.session_state.clear_history:
    st.session_state.clear_history=False
    st.experimental_rerun()
