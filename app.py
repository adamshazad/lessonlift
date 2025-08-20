# app.py
import streamlit as st
import google.generativeai as genai
import re
import base64
import sqlite3
from datetime import datetime, timezone
from io import BytesIO

# PDF tooling
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# ============== CONFIG =================
APP_TITLE = "📚 LessonLift - AI Lesson Planner"
DAILY_LIMIT = 50  # per user per day
DB_PATH = "lessonlift.db"
MODEL_NAME = "gemini-1.5-flash-latest"

# -------- Streamlit page setup ---------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --------- Global CSS (polish) ---------
st.markdown("""
<style>
body { background-color: white; color: black; }
.stTextInput>div>div>input, textarea, select {
  background-color: white !important;
  color: black !important;
  border: 1px solid #ccc !important;
  padding: 8px !important;
  border-radius: 6px !important;
}
.stCard {
  background-color: #f9f9f9 !important;
  color: black !important;
  border-radius: 12px !important;
  padding: 16px !important;
  margin-bottom: 12px !important;
  box-shadow: 0px 2px 8px rgba(0,0,0,0.12) !important;
  line-height: 1.55em !important;
}
.btn-row { display:flex; gap:10px; margin-top:10px; }
.btn-row a { text-decoration:none !important; }
.btn {
  padding:10px 16px;
  font-size:14px;
  border-radius:8px;
  border:none;
  background-color:#4CAF50;
  color:white !important;
  cursor:pointer;
  display:inline-block;
}
.small-muted { color:#666; font-size:12px; }
.center { display:flex; justify-content:center; }
</style>
""", unsafe_allow_html=True)

# ============== DB LAYER =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hashed_pw TEXT DEFAULT ''
      )
    """)
    c.execute("""
      CREATE TABLE IF NOT EXISTS usage(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date_utc TEXT NOT NULL,
        count INTEGER NOT NULL DEFAULT 0,
        UNIQUE(user_id, date_utc)
      )
    """)
    c.execute("""
      CREATE TABLE IF NOT EXISTS lessons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        created_utc TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
      )
    """)
    conn.commit()
    return conn

def get_or_create_user(conn, email, hashed_pw=""):
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    if row: return row[0]
    c.execute("INSERT INTO users(email, hashed_pw) VALUES(?,?)", (email, hashed_pw))
    conn.commit()
    return c.lastrowid

def get_usage_today(conn, user_id):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    c = conn.cursor()
    c.execute("SELECT count FROM usage WHERE user_id=? AND date_utc=?", (user_id, today))
    row = c.fetchone()
    return (row[0] if row else 0), today

def increment_usage(conn, user_id):
    count, today = get_usage_today(conn, user_id)
    c = conn.cursor()
    if count == 0:
        c.execute("INSERT OR IGNORE INTO usage(user_id, date_utc, count) VALUES(?,?,?)", (user_id, today, 0))
    c.execute("UPDATE usage SET count = count + 1 WHERE user_id=? AND date_utc=?", (user_id, today))
    conn.commit()

def store_lesson(conn, user_id, title, content):
    c = conn.cursor()
    c.execute("INSERT INTO lessons(user_id, created_utc, title, content) VALUES(?,?,?,?)",
              (user_id, datetime.now(timezone.utc).isoformat(), title, content))
    conn.commit()

def get_lessons(conn, user_id, limit=20):
    c = conn.cursor()
    c.execute("SELECT title, content, created_utc FROM lessons WHERE user_id=? ORDER BY id DESC LIMIT ?",
              (user_id, limit))
    return c.fetchall()

# ============== AUTH LAYER (placeholder) ==============
# ✅ Replace this section with Bolt.new auth later.
def fake_login_ui():
    st.markdown("### 🔐 Sign in")
    email = st.text_input("Email", placeholder="e.g. teacher@school.org")
    pw = st.text_input("Password", type="password", placeholder="Enter your password")
    # In production, validate pw with your identity provider (Bolt.new).
    login = st.button("Sign in")
    return email, pw, login

def ensure_logged_in(conn):
    if "user_id" in st.session_state and "user_email" in st.session_state:
        return True
    email, pw, login = fake_login_ui()
    if login:
        if not email or not pw:
            st.error("Please enter both email and password.")
            return False
        # Replace this with Bolt.new verification.
        user_id = get_or_create_user(conn, email)
        st.session_state["user_id"] = user_id
        st.session_state["user_email"] = email
        st.success("Signed in successfully.")
        return True
    return False

# ============== AI & PDF HELPERS =================
def strip_markdown(md_text: str) -> str:
    # keep headings and bullets if model returns markdown, but remove bold/italics markers and excessive ##/** lines
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', md_text)      # bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)             # italics
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)  # leading markdown headers
    # normalise double blank lines
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def create_pdf_wrapped(text: str) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50
    )
    styles = getSampleStyleSheet()
    # Slightly larger leading for clearer lists
    style = ParagraphStyle(
        "LessonText",
        parent=styles["Normal"],
        fontSize=11.5,
        leading=16,
    )
    # Preserve blank lines and bullet-like lines
    # Convert "- xxx" and "• xxx" to simple paragraphs (ReportLab basic Paragraph supports <br/>, not markdown bullets)
    paragraphs = []
    # Split by blank lines to keep spacing intentional
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            paragraphs.append(Spacer(1, 8))
            continue
        # Convert newlines within block to <br/>
        html_block = block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_block = html_block.replace("\n", "<br/>")
        paragraphs.append(Paragraph(html_block, style))
        paragraphs.append(Spacer(1, 8))

    doc.build(paragraphs)
    buffer.seek(0)
    return buffer

def render_download_buttons(plain_text: str, pdf_buf: BytesIO):
    txt_b64 = base64.b64encode(plain_text.encode("utf-8")).decode("utf-8")
    pdf_b64 = base64.b64encode(pdf_buf.read()).decode("utf-8")
    st.markdown(
        f"""
        <div class="btn-row">
          <a href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt"><span class="btn">⬇ Download TXT</span></a>
          <a href="data:application/pdf;base64,{pdf_b64}" download="lesson_plan.pdf"><span class="btn">⬇ Download PDF</span></a>
        </div>
        """,
        unsafe_allow_html=True
    )

def extract_and_render_sections(clean_output: str):
    # Show in tidy cards using common section headings if present
    sections = [
        "Lesson title","Learning outcomes","Starter activity","Main activity",
        "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
    ]
    # Case-insensitive search
    lower_text = clean_output.lower()
    indices = []
    for s in sections:
        i = lower_text.find(s.lower())
        if i != -1:
            indices.append((i, s))
    indices.sort(key=lambda x: x[0])

    if not indices:
        # Fall back: single card
        st.markdown(f"<div class='stCard'>{clean_output}</div>", unsafe_allow_html=True)
        return

    for idx, (start, title) in enumerate(indices):
        end = len(clean_output)
        if idx + 1 < len(indices):
            end = indices[idx + 1][0]
        section_text = clean_output[start:end].strip()
        # Light formatting: ensure a subtle title emphasis
        # If line starts with the heading, put it on its own line
        st.markdown(f"<div class='stCard'><strong>{title}</strong><br/>{section_text[len(title):].strip()}</div>", unsafe_allow_html=True)

# ============== APP CONTENT =================
def main():
    st.title(APP_TITLE)
    st.write("Generate tailored UK primary school lesson plans in seconds.")

    # Sidebar: your API key (kept on server; users don't need theirs)
    st.sidebar.title("🔑 Server API Key")
    api_key = st.sidebar.text_input("Your server's Gemini API Key", type="password")
    if not api_key:
        st.sidebar.info("Add your server API key here. Users will not see it.")
    else:
        genai.configure(api_key=api_key)

    # Optional logo
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Status**: App ready")
    st.sidebar.markdown("<span class='small-muted'>Your key is used server-side only.</span>", unsafe_allow_html=True)

    conn = init_db()

    # ---- Auth Gate (replace with Bolt.new later) ----
    if not ensure_logged_in(conn):
        st.stop()

    user_id = st.session_state["user_id"]
    user_email = st.session_state["user_email"]

    # Show today's usage
    used, today = get_usage_today(conn, user_id)
    st.info(f"👤 {user_email} — {used}/{DAILY_LIMIT} lessons generated today ({today}).")

    # --- Lesson form ---
    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        subject = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
        topic = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
        learning_objective = st.text_area(
            "Learning Objective (optional)",
            placeholder="e.g. Students will be able to add and subtract fractions with the same denominator."
        )
        ability_level = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_duration = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
        sen_notes = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Provide visual aids, simplified instructions, extra time.")
        submitted = st.form_submit_button("🚀 Generate Lesson Plan")

    if submitted:
        if not api_key:
            st.error("Server API key is missing. Add it in the sidebar to enable generation.")
        else:
            current_count, _ = get_usage_today(conn, user_id)
            if current_count >= DAILY_LIMIT:
                st.warning("⚠️ You have reached the maximum number of lessons for today. Please try again tomorrow.")
            else:
                # Compose prompt
                prompt = f"""Create a detailed UK primary school lesson plan with clear sections:
- Lesson title
- Learning outcomes (bulleted)
- Starter activity (step-by-step)
- Main activity (step-by-step, include differentiation)
- Plenary activity (brief)
- Resources needed (bulleted)
- Differentiation ideas (bulleted)
- Assessment methods (bulleted)

Use concise bullets where appropriate. Avoid markdown headings like ## or ** in the output.

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN/EAL Notes: {sen_notes or 'None'}
"""
                try:
                    with st.spinner("✨ Creating lesson plan..."):
                        model = genai.GenerativeModel(MODEL_NAME)
                        resp = model.generate_content(prompt)
                        raw = (resp.text or "").strip()
                        clean = strip_markdown(raw)

                    # Save lesson + increment usage
                    title_for_history = f"{subject} – {topic} ({year_group})"
                    store_lesson(conn, user_id, title_for_history, clean)
                    increment_usage(conn, user_id)

                    # Render sections and full text
                    extract_and_render_sections(clean)
                    st.text_area("Full Lesson Plan (copyable)", value=clean, height=380)

                    # Create PDF + downloads
                    pdf_buf = create_pdf_wrapped(clean)
                    render_download_buttons(clean, pdf_buf)

                except Exception as e:
                    # Most common: API quota exceeded on your server key
                    st.error("Could not generate a lesson right now. This often happens when the server API quota has been reached. Please try again later.")
                    st.caption(f"Technical detail (for you): {e}")

    # --- Regeneration controls ---
    st.markdown("### 🔄 Not happy with the plan?")
    col1, col2 = st.columns(2)
    with col1:
        regen_style = st.selectbox(
            "Regeneration style",
            [
                "♻️ Just regenerate (different variation)",
                "🎨 More creative & engaging activities",
                "📋 More structured with timings",
                "🧩 Simplify for lower ability",
                "🚀 Challenge for higher ability"
            ]
        )
    with col2:
        custom_instruction = st.text_input("Custom instruction (optional)", placeholder="e.g. Include an outdoor activity")

    if st.button("🔁 Regenerate Lesson Plan"):
        if not api_key:
            st.error("Server API key is missing. Add it in the sidebar to enable generation.")
        else:
            current_count, _ = get_usage_today(conn, user_id)
            if current_count >= DAILY_LIMIT:
                st.warning("⚠️ You have reached the maximum number of lessons for today. Please try again tomorrow.")
            else:
                base = f"""Regenerate the previous lesson plan, keeping the same year group, subject, and topic, but apply these changes:
- Use concise bullet points where appropriate.
- Keep sections clear and scannable (no markdown ## or **).
"""
                if custom_instruction:
                    base += f"- Additional instruction: {custom_instruction}\n"
                    regen_msg = f"Lesson updated: {custom_instruction}"
                else:
                    mapping = {
                        "🎨 More creative & engaging activities": "Make activities more creative, interactive, and fun.",
                        "📋 More structured with timings": "Add clear structure with suggested timings per section.",
                        "🧩 Simplify for lower ability": "Simplify language and provide more scaffolding and modelling.",
                        "🚀 Challenge for higher ability": "Add stretch/challenge tasks and deeper thinking questions.",
                        "♻️ Just regenerate (different variation)": "Provide a fresh variation."
                    }
                    base += f"- Style: {mapping.get(regen_style, 'Provide a fresh variation.')}\n"
                    regen_msg = "Here’s a new updated version of your lesson plan."

                try:
                    with st.spinner("✨ Regenerating..."):
                        model = genai.GenerativeModel(MODEL_NAME)
                        resp = model.generate_content(base)
                        raw = (resp.text or "").strip()
                        clean = strip_markdown(raw)

                    # Save + increment usage
                    store_lesson(conn, user_id, f"Regenerated – {datetime.now().strftime('%H:%M')}", clean)
                    increment_usage(conn, user_id)

                    st.info(f"🔄 {regen_msg}")
                    extract_and_render_sections(clean)
                    st.text_area("Full Lesson Plan (copyable)", value=clean, height=380)
                    pdf_buf = create_pdf_wrapped(clean)
                    render_download_buttons(clean, pdf_buf)

                except Exception as e:
                    st.error("Could not regenerate the lesson right now (likely server API quota). Please try again later.")
                    st.caption(f"Technical detail (for you): {e}")

    # --- Sidebar: History for this user ---
    st.sidebar.markdown("## 📚 Your Lesson History")
    rows = get_lessons(conn, user_id, limit=12)
    if rows:
        for title, content, created in rows:
            st.sidebar.markdown(f"**{title}**  \n<span class='small-muted'>{created[:10]}</span>", unsafe_allow_html=True)
            st.sidebar.markdown(f"<span class='small-muted'>{content[:80]}...</span>", unsafe_allow_html=True)
            st.sidebar.markdown("---")
    else:
        st.sidebar.info("No lessons yet.")

if __name__ == "__main__":
    main()