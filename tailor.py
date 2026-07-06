import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# 系统提示：定义角色 + 规则 + 护栏。这部分稳定不变。
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
        messages=[
            {"role": "user", "content": user_prompt}
        ],
    )
    # content 可能包含 thinking 块和 text 块，只取 text 块
    text_parts = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_parts)


if __name__ == "__main__":
    print("=== 简历要点定制工具 ===\n")
    print("请粘贴目标岗位的 Job Description，粘贴完按回车再输入 END 单独一行结束：\n")
    jd_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        jd_lines.append(line)
    job_description = "\n".join(jd_lines)

    print("\n现在粘贴你的相关经历（同样，输完单独一行输入 END 结束）：\n")
    exp_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        exp_lines.append(line)
    experience = "\n".join(exp_lines)

    print("\n正在生成定制要点...\n")
    result = tailor_bullets(job_description, experience)
    print(result)