"""Generate a concise daily digest from analyzed emails and action items."""
from app import llm

DIGEST_PROMPT = (
    "你是企业主的中文晨报助手。请基于提供的邮件清单与待办列表，输出全简体中文、结构化 Markdown 晨报：\n\n"
    "## 📊 今日邮件总览\n- 总数 / 待办\n\n"
    "## 🔴 紧急待办（今天处理）\n- [发件人]：诉求（≤15字）（优先级）\n\n"
    "## 🟡 重要跟进（本周内）\n- [发件人]：一句话要点\n\n"
    "## ⚪ 其余信息流\n- 一句话概括资讯/订阅/系统通知类邮件。\n\n"
    "规则：全中文、简洁可扫读；客户投诉与商机线索排最前；不要编造邮件里没有的信息。"
)


def _compile(emails, todos):
    lines = []
    for e in emails:
        lines.append(
            f"发件人: {e.get('sender', '')}\n主题: {e.get('subject', '')}\n摘要: {(e.get('summary_zh') or e.get('summary') or '')[:200]}"
        )
    email_text = "\n---\n".join(lines) or "(今日无邮件)"
    todo_lines = [f"- [{t.get('sender','')}] {t.get('subject','')}（{t.get('priority','')}）" for t in todos]
    todo_text = "\n".join(todo_lines) or "(无待办)"
    return email_text, todo_text


def generate(emails, todos):
    """emails/todos 为 dict 列表，返回中文晨报字符串。"""
    email_text, todo_text = _compile(emails, todos)
    user = f"今日邮件（共 {len(emails)} 封）：\n\n{email_text}\n\n当前 P0/P1 待办：\n{todo_text}"
    return llm.chat_text(DIGEST_PROMPT, user, temperature=0.3, max_tokens=1500)
