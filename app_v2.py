import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv
from anthropic import Anthropic

st.set_page_config(page_title="Resume Tailor", page_icon="✦", layout="wide")

load_dotenv()
client = Anthropic()

SYSTEM_PROMPT = """You are an expert resume editor. You will be given a candidate's full resume and a target job description. Your job is to tailor the resume to the target role.

What to KEEP UNCHANGED (do not edit these sections at all — reproduce them exactly as given):
- The Education section (schools, degrees, GPA, coursework, dates)
- The contact information and name

What to TAILOR (this is where you focus):
- The Summary statement: adjust emphasis to align with the target role, using only facts already true in the resume.
- The Projects section: reorder projects so the most relevant to the job appear first, and strengthen the wording of relevant bullet points.
- The Skills section: you may reorder to surface the most relevant skills first, but do NOT add or remove any skill.

Rules you MUST follow:
- NEVER invent, add, or exaggerate any facts. Only use experience, skills, projects, and numbers already in the resume.
- Never fabricate numbers; keep real numbers as-is.
- Keep the resume's existing section structure. Do not invent new sections.
- Use strong action verbs and concise, results-oriented phrasing.
- Output the tailored resume as clean, readable text, organized by section. No preamble or explanation — output only the tailored resume."""

def tailor_resume(resume_text: str, job_description: str, include_skills: bool) -> str:
    # 根据是否优化 Skills，给出不同的指令
    if include_skills:
        skills_instruction = "- SKILLS: you may reorder to surface the most relevant skills first, but do NOT add or remove any skill."
    else:
        skills_instruction = "- SKILLS: keep exactly as in the original resume; do not change it."

    system_prompt = f"""You are an expert resume editor. You will be given a candidate's full resume and a target job description. Produce a tailored version of the FULL resume for the target role.

Output the COMPLETE resume, keeping all original sections in their original order (e.g., Summary, Education, Skills, Projects). Handle each section as follows:
- CONTACT INFO and EDUCATION: reproduce exactly as given; do not edit at all.
- SUMMARY: adjust emphasis to align with the target role, using only facts already true in the resume.
{skills_instruction}
- PROJECTS: reorder so the most relevant projects appear first, and strengthen the wording of relevant bullet points.

Rules you MUST follow:
- NEVER invent, add, or exaggerate any facts. Only use experience, skills, projects, and numbers already in the resume.
- Never fabricate numbers; keep real numbers as-is.
- Do not invent new sections or drop existing ones.
- Use strong action verbs and concise, results-oriented phrasing.
- Output the complete tailored resume as clean, readable text organized by section. No preamble or explanation — output only the resume."""

    user_prompt = f"""TARGET JOB DESCRIPTION:
{job_description}

CANDIDATE'S CURRENT RESUME:
{resume_text}

Now produce the complete tailored resume."""

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text_parts = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_parts)

import json

def analyze_match(resume_text: str, job_description: str) -> dict:
    system_prompt = """You are a resume-matching analyzer. Given a job description and a resume, identify the key skills and requirements in the job description, then assess how well the resume covers them.

Respond with ONLY a valid JSON object (no markdown, no code fences, no explanation) in exactly this format:
{
  "keywords": ["skill1", "skill2", "..."],
  "matched": ["skill1", "..."],
  "missing": ["skill2", "..."],
  "score": 75
}

Where:
- "keywords": the key skills/requirements you extracted from the job description (aim for 8-15).
- "matched": which of those keywords the resume clearly demonstrates (judge by meaning, not exact wording — e.g., "ML" matches "machine learning").
- "missing": which keywords the resume does not clearly cover.
- "score": an integer 0-100 = (number matched / total keywords) * 100, rounded."""

    user_prompt = f"""JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Analyze the match and respond with only the JSON object."""

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    return json.loads(text)

# ---------- PDF 读取函数 ----------
def extract_pdf_text(uploaded_file):
    """接收上传的 PDF 文件，逐页提取文字并拼接返回。"""
    reader = PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(233,64,120,0.10) 0%, transparent 22%),
            radial-gradient(circle at 88% 15%, rgba(255,180,60,0.10) 0%, transparent 20%),
            radial-gradient(circle at 78% 82%, rgba(120,90,200,0.08) 0%, transparent 22%),
            radial-gradient(circle at 20% 85%, rgba(70,180,160,0.08) 0%, transparent 20%),
            linear-gradient(160deg, #ffffff 0%, #f5f6f8 100%);
    }
    .stApp, .stApp p, .stApp span, .stApp label { color: #4a4550; }
    .hero { padding: 2.2rem 0 1.3rem 0; border-bottom: 1px solid rgba(120,110,130,0.14); margin-bottom: 1.8rem; }
    .hero-badge {
        display: inline-block; font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase;
        color: #d6396f; background: rgba(233,64,120,0.08);
        border: 1px solid rgba(233,64,120,0.28); border-radius: 999px;
        padding: 0.3rem 0.9rem; margin-bottom: 1rem;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); cursor: default;
    }
    .hero-badge:hover { transform: scale(1.06); background: rgba(233,64,120,0.16); box-shadow: 0 4px 18px rgba(233,64,120,0.3); letter-spacing: 0.22em; }
    .hero-title { font-size: 2.4rem; font-weight: 700; color: #2f2b38; margin: 0; line-height: 1.15; letter-spacing: -0.01em; }
    .hero-title .accent {
        background: linear-gradient(120deg, #e94078 0%, #f7a13d 55%, #7a5ac8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .hero-sub { color: #837d8c; font-size: 1rem; margin-top: 0.6rem; white-space: nowrap; }
    .stTextArea textarea {
        background: rgba(255,255,255,0.85) !important;
        border: 1px solid rgba(120,110,130,0.2) !important;
        border-radius: 14px !important;
        color: #4a4550 !important; font-size: 0.9rem !important;
        box-shadow: 0 2px 12px rgba(120,110,130,0.06) !important;
        transition: transform 0.3s cubic-bezier(0.34, 1.4, 0.64, 1), box-shadow 0.3s ease, border-color 0.3s ease !important;
    }
    /* ---------- 文本框：彩色衬底卡片 + 悬停放大 ---------- */
    .stTextArea {
        border-radius: 18px;
        padding: 4px;
        /* 彩色渐变衬底，让框像浮在一层柔和底图上 */
        background: linear-gradient(135deg, rgba(233,64,120,0.12), rgba(247,161,61,0.10) 50%, rgba(122,90,200,0.12));
        box-sizing: border-box;      /* 让 padding 算在宽度内，不撑宽 */
        max-width: 100%;
        overflow: hidden;            /* 裁掉多余、去掉横向滚动条 */
    }
    .stTextArea textarea {
        background: rgba(255,255,255,0.92) !important;
        border: none !important;
        border-radius: 14px !important;
        color: #4a4550 !important; font-size: 0.9rem !important;
        box-shadow: inset 0 1px 3px rgba(120,110,130,0.06) !important;
        overflow-x: hidden !important;   /* 去掉横向滚动条 */
        resize: vertical !important;     /* 只能上下拉 */
        box-sizing: border-box !important;
    }
    .stTextArea textarea:focus {
        box-shadow: inset 0 1px 3px rgba(120,110,130,0.06), 0 0 0 3px rgba(233,64,120,0.18) !important;
    }
    .stTextArea textarea::placeholder { color: #b8b2c0 !important; }

    /* ---------- 上传框：同款彩色衬底 + 悬停放大 ---------- */
    [data-testid="stFileUploader"] section {
        border-radius: 16px !important;
        border: 2px dashed rgba(233,64,120,0.35) !important;
        background: linear-gradient(135deg, rgba(233,64,120,0.06), rgba(247,161,61,0.05)) !important;
        transition: transform 0.3s cubic-bezier(0.34, 1.4, 0.64, 1), box-shadow 0.3s ease, border-color 0.3s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        transform: scale(1.02);
        border-color: rgba(233,64,120,0.6) !important;
        box-shadow: 0 12px 34px rgba(120,110,130,0.16) !important;
    }
    .stButton > button:hover { transform: translateY(-2px) scale(1.01); box-shadow: 0 10px 28px rgba(233,64,120,0.45); letter-spacing: 0.03em; }
    .stButton > button:active { transform: translateY(0) scale(0.99); }
    /* 圆环进度 */
    .ring-wrap { position: relative; width: 120px; margin: 0.5rem auto; text-align: center; }
    .ring { width: 120px; height: 120px; transform: rotate(-90deg); }
    .ring-bg { fill: none; stroke: rgba(120,110,130,0.12); stroke-width: 10; }
    .ring-fg {
        fill: none; stroke-width: 10; stroke-linecap: round;
        stroke-dashoffset: 326.7;               /* 起点：整圈藏起 */
        animation: fillRing 1.3s cubic-bezier(0.34, 1.2, 0.64, 1) forwards;
    }
    /* 动画：从整圈藏起，转到目标分数位置 */
    @keyframes fillRing {
        from { stroke-dashoffset: 326.7; }
        to   { stroke-dashoffset: var(--target-offset); }
    }
    .ring-before { stroke: #c3bcc9; }
    .ring-after  { stroke: #e94078; }          /* 先用纯色，稳定可靠 */
    /* 悬停时整体放大一点，增加交互感 */
    .ring-wrap:hover .ring { transform: rotate(-90deg) scale(1.05); transition: transform 0.3s ease; }
    .ring-score { position: absolute; top: 42px; left: 0; right: 0; font-size: 1.9rem; font-weight: 800; color: #2f2b38; }
    .ring-pct { font-size: 1rem; font-weight: 600; color: #837d8c; }
    .ring-label { font-size: 0.85rem; font-weight: 600; color: #837d8c; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.2rem; }
    /* ---------- 整条标题做成渐变卡片 ---------- */
    .field-label {
        display: inline-flex; align-items: center; gap: 0.7rem;
        font-size: 1.05rem; font-weight: 700; color: #fff;
        margin: 1.4rem 0 0.9rem 0;
        padding: 0.55rem 1.3rem 0.55rem 0.6rem;
        border-radius: 999px;
        background: linear-gradient(120deg, #e94078 0%, #f7743d 100%);
        box-shadow: 0 6px 18px rgba(233,64,120,0.35);
        transition: all 0.35s cubic-bezier(0.34, 1.4, 0.64, 1);
    }
    .field-label:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 10px 26px rgba(233,64,120,0.5);
    }
    .field-num {
        display: inline-flex; align-items: center; justify-content: center;
        width: 28px; height: 28px; border-radius: 50%;
        background: rgba(255,255,255,0.95);
        color: #e94078; font-size: 0.9rem; font-weight: 800;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .field-label:hover .field-num {
        transform: rotate(12deg) scale(1.12);
    }
    /* 治外层容器超宽导致的横向滚动条 */
    .stTextArea {
        box-sizing: border-box !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    div[data-testid="stTextArea"] {
        box-sizing: border-box !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }
    .kw-title { font-size: 0.85rem; font-weight: 700; color: #837d8c; text-transform: uppercase; letter-spacing: 0.06em; margin: 0.5rem 0; }
    .tag-row { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .tag { display: inline-block; font-size: 0.82rem; padding: 0.3rem 0.7rem; border-radius: 999px; font-weight: 500; }
    .tag-matched { background: rgba(70,180,160,0.14); color: #2f9e86; border: 1px solid rgba(70,180,160,0.3); }
    .tag-missing { background: rgba(120,110,130,0.08); color: #9a94a3; border: 1px solid rgba(120,110,130,0.2); }
    .tag-new {
        background: linear-gradient(120deg, #f7a13d, #e94078);
        color: #fff !important; border: none !important;
        box-shadow: 0 2px 8px rgba(233,64,120,0.35); font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <span class="hero-badge">✦ AI-Powered · Claude API</span>
    <h1 class="hero-title">Resume <span class="accent">Tailor</span></h1>
    <p class="hero-sub">Upload your resume and paste a job description — get a tailored version, 
    with a before-and-after match score.</p>
</div>
""", unsafe_allow_html=True)

def generate_cover_letter(resume_text: str, job_description: str) -> str:
    system_prompt = """You are helping a job seeker write a cover letter. You will be given their resume and a target job description.

Write a concise, professional cover letter (about 4 short paragraphs) following these principles:

- LEAD WITH STRENGTHS: open by connecting the candidate's most relevant real experience to what the role needs.
- BE HONEST: only use experience, skills, and projects that actually appear in the resume. NEVER invent or exaggerate anything. Do not claim skills or experience the resume does not show.
- HANDLE GAPS BRIEFLY: if the candidate clearly lacks something the role wants, do not dwell on it or list weaknesses. At most, close with a single confident line about being a fast learner — do not enumerate what they can't do.
- TONE: warm, direct, and confident, not boastful or generic. Avoid clichés like "I am writing to express my interest."
- Keep it under 300 words. Address it to "Dear Hiring Manager,". End with "Sincerely," and leave the name blank as [Your Name].

Output only the cover letter text. No preamble or explanation."""

    user_prompt = f"""TARGET JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{resume_text}

Write the tailored cover letter."""

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text_parts = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_parts)

# ---------- 界面：先 JD，再上传简历（上下堆叠）----------
st.markdown('<div class="field-label"><span class="field-num">1</span> Job Description</div>', unsafe_allow_html=True)
job_description = st.text_area(
    "Paste the job description", height=250, label_visibility="collapsed",
    placeholder="Paste the target job description here...",
)

st.markdown('<div class="field-label"><span class="field-num">2</span> Your Resume (PDF)</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your resume", type="pdf", label_visibility="collapsed")

# ---------- 读取 PDF、显示预览、生成优化版 ----------
if uploaded_file is not None:
    resume_text = extract_pdf_text(uploaded_file)

    with st.expander("Preview extracted resume text"):
        st.text(resume_text)

    include_skills = st.checkbox("Also tailor my Skills section")
    include_cover = st.checkbox("Also generate a cover letter")

    if st.button("Tailor My Resume", type="primary"):
        if not job_description.strip():
            st.warning("Please paste the job description first.")
        else:
            with st.spinner("Tailoring your resume to the role..."):
                result = tailor_resume(resume_text, job_description, include_skills)
            st.markdown('<div class="section-heading">✦ Tailored Result</div>', unsafe_allow_html=True)
            st.text_area("result", result, height=500, label_visibility="collapsed")

            # ---- 匹配度分析：分别算修改前和修改后 ----
            with st.spinner("Analyzing match scores..."):
                before = analyze_match(resume_text, job_description)
                after = analyze_match(result, job_description)

            st.markdown('<div class="section-heading">✦ Match Score: Before → After</div>', unsafe_allow_html=True)

            CIRC = 326.7

            def ring_html(score, label, use_gradient):
                offset = CIRC * (1 - score / 100)
                # After 用渐变描边，Before 用灰色
                stroke = "url(#ringGrad)" if use_gradient else "#c3bcc9"
                # 每个圆环用唯一的渐变 id，避免两个 SVG 冲突
                return f"""
                <div class="ring-wrap">
                    <svg class="ring" viewBox="0 0 120 120">
                        <defs>
                            <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#7a2ff7"/>
                                <stop offset="100%" stop-color="#e94078"/>
                            </linearGradient>
                        </defs>
                        <circle class="ring-bg" cx="60" cy="60" r="52"/>
                        <circle class="ring-fg" cx="60" cy="60" r="52"
                            stroke="{stroke}"
                            stroke-dasharray="{CIRC}"
                            style="--target-offset: {offset};"/>
                    </svg>
                    <div class="ring-score">{score}<span class="ring-pct">%</span></div>
                    <div class="ring-label">{label}</div>
                </div>
                """

            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown(ring_html(before["score"], "Before", use_gradient=False), unsafe_allow_html=True)
            with c2:
                st.markdown(ring_html(after["score"], "After", use_gradient=True), unsafe_allow_html=True)

            # ---- 分数变化提示 ----
            delta = after["score"] - before["score"]
            if delta > 0:
                st.success(f"Match improved by {delta} points.")
            elif delta == 0:
                st.info("Match score unchanged.")
            else:
                st.warning(f"Match score dropped by {abs(delta)} points.")

            # ---- 前后关键词对比 ----
            newly_matched = [k for k in after["matched"] if k not in before["matched"]]

            def tags_html(matched, missing, highlight):
                html = ""
                for k in matched:
                    cls = "tag-new" if k in highlight else "tag-matched"
                    mark = "★" if k in highlight else "✓"
                    html += f'<span class="tag {cls}">{mark} {k}</span>'
                for k in missing:
                    html += f'<span class="tag tag-missing">✗ {k}</span>'
                return html

            st.markdown('<div class="section-heading">Keyword Coverage: Before → After</div>', unsafe_allow_html=True)
            cc1, cc2 = st.columns(2, gap="large")
            with cc1:
                st.markdown('<div class="kw-title">Before tailoring</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-row">{tags_html(before["matched"], before["missing"], [])}</div>', unsafe_allow_html=True)
            with cc2:
                st.markdown('<div class="kw-title">After tailoring</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-row">{tags_html(after["matched"], after["missing"], newly_matched)}</div>', unsafe_allow_html=True)

            if newly_matched:
                st.success("Newly covered after tailoring: " + ", ".join(newly_matched))
            
            # ---- 可选：生成 cover letter ----
            if include_cover:
                st.markdown('<div class="section-heading">✦ Cover Letter</div>', unsafe_allow_html=True)
                with st.spinner("Writing your cover letter..."):
                    cover = generate_cover_letter(resume_text, job_description)
                st.text_area("cover", cover, height=400, label_visibility="collapsed")