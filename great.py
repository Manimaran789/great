import streamlit as st
from datetime import date, timedelta
from PyPDF2 import PdfReader

# ===================== STYLE =====================

def app_header():
    st.markdown("""
        <h1 style='text-align:center; color:#4CAF50;'>📚 AI Study Planner</h1>
        <p style='text-align:center; font-size:16px;'>
        Upload syllabus • Generate plan • Track progress
        </p>
        <hr>
    """, unsafe_allow_html=True)

# ===================== PDF ANALYSIS =====================

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def extract_topics_from_text(text):
    lines = text.split("\n")
    topics = []

    for line in lines:
        clean = line.strip()
        if 3 < len(clean) < 80:  # filter noise
            topics.append(clean)

    return list(set(topics))  # remove duplicates

# ===================== LOGIC =====================

def generate_study_plan(topics, exam_date):
    today = date.today()
    days_left = (exam_date - today).days

    if days_left <= 0 or not topics:
        return {}

    plan = {}
    topics_per_day = max(1, len(topics) // days_left + 1)

    index = 0
    for day in range(days_left):
        if index >= len(topics):
            break

        study_date = today + timedelta(days=day)
        plan[study_date] = topics[index:index + topics_per_day]
        index += topics_per_day

    return plan

# ===================== SESSION STATE =====================

def init_state():
    if "completed" not in st.session_state:
        st.session_state.completed = []

def mark_done(topic):
    if topic not in st.session_state.completed:
        st.session_state.completed.append(topic)

def is_done(topic):
    return topic in st.session_state.completed

# ===================== STREAMLIT APP =====================

st.set_page_config(page_title="AI Study Planner", layout="centered")

init_state()
app_header()

st.subheader("📂 Upload Syllabus PDF")
pdf_file = st.file_uploader("Upload your syllabus (PDF only)", type=["pdf"])

st.subheader("📅 Select Exam Date")
exam_date = st.date_input("")

topics = []

if pdf_file:
    with st.spinner("Analyzing PDF..."):
        text = extract_text_from_pdf(pdf_file)
        topics = extract_topics_from_text(text)

    st.success(f"Extracted {len(topics)} topics from PDF")

    with st.expander("📄 View Extracted Topics"):
        for t in topics[:30]:
            st.write("-", t)

if st.button("🚀 Generate Study Plan"):
    plan = generate_study_plan(topics, exam_date)

    if not plan:
        st.error("❌ Upload valid PDF and choose a future exam date.")
    else:
        st.success("✅ Study plan generated!")

        for study_day, day_topics in plan.items():
            st.markdown(f"### 🗓 {study_day}")

            for topic in day_topics:
                if st.checkbox(
                    topic,
                    value=is_done(topic),
                    key=f"{study_day}-{topic}"
                ):
                    mark_done(topic)

# ===================== PROGRESS =====================

st.markdown("---")
st.subheader("📊 Progress Summary")
st.write(f"✔ Completed topics: {len(st.session_state.completed)}")

if st.session_state.completed:
    st.write(st.session_state.completed)
else:
    st.info("No topics completed yet.")
