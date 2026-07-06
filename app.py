import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

SYSTEM_PROMPT = """You are an expert resume writer helping a job seeker tailor their experience to a specific job description.

Your task: rewrite the candidate's raw experience into 3-4 strong, tailored resume bullet points that align with the target job description.

Rules you MUST follow:
- Only use facts present in the candidate's provided experience. NEVER invent skills, tools, metrics, or accomplishments the candidate did not mention.
- Emphasize the parts of their real experience most relevant to the job description.
- Start each bullet with a strong action verb.
- Where the candidate gave real numbers, keep them. Do not fabricate numbers.
- Keep each bullet concise (one to two lines).
- Output ONLY the bullet points, each starting with "- ". No preamble, no explanation."""


def tailor_bullets(job_description: str, experience: str) -> str:
    user_prompt = f"""JOB DESCRIPTION:
{job_description}

CANDIDATE'S RAW EXPERIENCE:
{experience}

Now write the tailored resume bullet points."""

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text_parts = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_parts)


st.set_page_config(page_title="Job Application Assistant", page_icon="✦", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    /* 干净浅底 + 角落若隐若现的彩色光点，呼应参考图 */
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(233,64,120,0.10) 0%, transparent 22%),
            radial-gradient(circle at 88% 15%, rgba(255,180,60,0.10) 0%, transparent 20%),
            radial-gradient(circle at 78% 82%, rgba(120,90,200,0.08) 0%, transparent 22%),
            radial-gradient(circle at 20% 85%, rgba(70,180,160,0.08) 0%, transparent 20%),
            linear-gradient(160deg, #ffffff 0%, #f5f6f8 100%);
    }
    .stApp, .stApp p, .stApp span, .stApp label { color: #4a4550; }

    /* ---------- 标题区 ---------- */
    .hero { padding: 2.2rem 0 1.3rem 0; border-bottom: 1px solid rgba(120,110,130,0.14); margin-bottom: 1.8rem; }
    .hero-badge {
        display: inline-block; font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase;
        color: #d6396f; background: rgba(233,64,120,0.08);
        border: 1px solid rgba(233,64,120,0.28); border-radius: 999px;
        padding: 0.3rem 0.9rem; margin-bottom: 1rem;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); cursor: default;
    }
    .hero-badge:hover {
        transform: scale(1.06); background: rgba(233,64,120,0.16);
        box-shadow: 0 4px 18px rgba(233,64,120,0.3); letter-spacing: 0.22em;
    }
    .hero-title { font-size: 2.4rem; font-weight: 700; color: #2f2b38; margin: 0; line-height: 1.15; letter-spacing: -0.01em; }
    .hero-title .accent {
        background: linear-gradient(120deg, #e94078 0%, #f7a13d 55%, #7a5ac8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .hero-sub { color: #837d8c; font-size: 1rem; margin-top: 0.6rem; max-width: 640px; }

    /* ---------- 输入框标签 + 序号图标（彩色圆点感） ---------- */
    .field-label { display: flex; align-items: center; gap: 0.55rem; font-size: 0.9rem; font-weight: 600; color: #5a5462; margin-bottom: 0.5rem; }
    .field-num {
        display: inline-flex; align-items: center; justify-content: center;
        width: 24px; height: 24px; border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, #f57ba0, #e94078);
        color: #fff; font-size: 0.78rem; font-weight: 700;
        box-shadow: 0 2px 8px rgba(233,64,120,0.35);
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .field-label:hover .field-num {
        transform: rotate(10deg) scale(1.2);
        box-shadow: 0 4px 16px rgba(233,64,120,0.55);
    }

    /* ---------- 文本域 ---------- */
    .stTextArea textarea {
        background: rgba(255,255,255,0.85) !important;
        border: 1px solid rgba(120,110,130,0.2) !important;
        border-radius: 14px !important;
        color: #4a4550 !important; font-size: 0.9rem !important;
        box-shadow: 0 2px 12px rgba(120,110,130,0.06) !important;
        transition: transform 0.3s cubic-bezier(0.34, 1.4, 0.64, 1),
                    box-shadow 0.3s ease, border-color 0.3s ease !important;
    }
    .stTextArea textarea:hover {
        transform: scale(1.015);
        border-color: rgba(233,64,120,0.4) !important;
        box-shadow: 0 10px 30px rgba(120,110,130,0.14) !important;
    }
    .stTextArea textarea:focus {
        transform: scale(1.03);
        border-color: #e94078 !important;
        box-shadow: 0 0 0 3px rgba(233,64,120,0.15), 0 14px 40px rgba(120,110,130,0.18) !important;
    }
    .stTextArea textarea::placeholder { color: #b8b2c0 !important; }

    /* ---------- 主按钮（多彩渐变） ---------- */
    .stButton > button {
        background: linear-gradient(120deg, #e94078 0%, #f7743d 100%);
        color: #fff; border: none; border-radius: 12px;
        padding: 0.65rem 1.5rem; font-weight: 600; font-size: 0.95rem; width: 100%;
        box-shadow: 0 4px 14px rgba(233,64,120,0.28);
        transition: all 0.3s cubic-bezier(0.34, 1.4, 0.64, 1);
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 10px 28px rgba(233,64,120,0.45);
        letter-spacing: 0.03em;
    }
    .stButton > button:active { transform: translateY(0) scale(0.99); }

    /* ---------- 结果卡片 ---------- */
    .result-card {
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(120,110,130,0.14);
        border-left: 3px solid #e94078;
        border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;
        color: #4a4550; font-size: 0.92rem; line-height: 1.55;
        box-shadow: 0 2px 12px rgba(120,110,130,0.06);
        transition: all 0.3s cubic-bezier(0.34, 1.4, 0.64, 1);
        animation: fadeIn 0.4s ease;
    }
    .result-card:nth-child(2) { border-left-color: #f7a13d; }
    .result-card:nth-child(3) { border-left-color: #7a5ac8; }
    .result-card:nth-child(4) { border-left-color: #46b4a0; }
    .result-card:hover {
        transform: translateX(6px);
        border-left-width: 6px;
        box-shadow: 0 10px 26px rgba(120,110,130,0.16);
    }
    @keyframes fadeIn { from {opacity:0; transform:translateY(8px);} to {opacity:1; transform:translateY(0);} }

    .section-heading { font-size: 1.1rem; font-weight: 700; color: #2f2b38; margin: 0.5rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <span class="hero-badge">✦ AI-Powered · Claude API</span>
    <h1 class="hero-title">Job Application <span class="accent">Assistant</span></h1>
    <p class="hero-sub">Paste a job description and your raw experience. Get tailored resume 
    bullet points — grounded strictly in your real background.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="field-label"><span class="field-num">1</span> Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area("jd", height=300, label_visibility="collapsed",
        placeholder="Paste the target job description here...")
    st.caption(f"{len(job_description)} characters")

with col2:
    st.markdown('<div class="field-label"><span class="field-num">2</span> Your Raw Experience</div>', unsafe_allow_html=True)
    experience = st.text_area("exp", height=300, label_visibility="collapsed",
        placeholder="Paste your projects, skills, and past experience...")
    st.caption(f"{len(experience)} characters")

st.write("")
generate = st.button("✦  Generate Tailored Bullets", type="primary")

if generate:
    if not job_description.strip() or not experience.strip():
        st.warning("Please fill in both fields before generating.")
    else:
        with st.spinner("Analyzing the role and tailoring your experience..."):
            result = tailor_bullets(job_description, experience)
        st.success("Done — here are your tailored bullets.")
        st.markdown('<div class="section-heading">✦ Tailored Resume Bullets</div>', unsafe_allow_html=True)
        bullets = [line.strip().lstrip("-").strip() for line in result.split("\n") if line.strip()]
        for b in bullets:
            st.markdown(f'<div class="result-card">{b}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Copy all</div>', unsafe_allow_html=True)
        st.code("\n".join(f"• {b}" for b in bullets), language=None)