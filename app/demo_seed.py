"""Synthetic, non-personal dataset for the public course demonstration."""
from datetime import datetime, timedelta, timezone

from app import actions, db, knowledge, topics


DEMO_EMAILS = [
    {
        "trace_id": "public-demo-course-1", "sender": "course-platform@example.edu",
        "subject": "AI Automation: team project submission instructions",
        "intent": "EDUCATION_NOTICE", "category": "教育通知", "priority": "P1_HIGH",
        "summary": "The course team project requires a five-minute demo video and repository link by Friday.",
        "summary_zh": "课程小组项目要求在周五前提交五分钟演示视频和代码仓库链接。",
        "requires_action": True, "deadline_days": 4,
        "action": "Submit the project video and repository link",
        "evidence": "Please submit a five-minute demo video and repository link by Friday.",
    },
    {
        "trace_id": "public-demo-hackathon-1", "sender": "organizer@innovation-lab.example",
        "subject": "Agent Hackathon: final presentation update",
        "intent": "PROJECT_UPDATE", "category": "项目动态", "priority": "P1_HIGH",
        "summary": "Finalist teams present on 12 October; slides must use the supplied template.",
        "summary_zh": "入围团队将于10月12日展示，幻灯片必须使用主办方模板。",
        "requires_action": True, "deadline_days": 8,
        "action": "Prepare the finalist presentation using the official template",
        "evidence": "Finalist teams must use the official slide template for the 12 October presentation.",
    },
    {
        "trace_id": "public-demo-subscription-1", "sender": "billing@cloudnotes.example",
        "subject": "CloudNotes Pro renewal reminder",
        "intent": "PAYMENT_BILLING", "category": "账单付款", "priority": "P3_LOW",
        "summary": "CloudNotes Pro renews next month at $12 per month unless cancelled.",
        "summary_zh": "CloudNotes Pro 将于下月按每月12美元续订，可在续订前取消。",
        "requires_action": False,
    },
    {
        "trace_id": "public-demo-security-1", "sender": "security@accounts.example",
        "subject": "New sign-in detected",
        "intent": "SECURITY_ALERT", "category": "安全提醒", "priority": "P0_CRITICAL",
        "summary": "A new sign-in was detected. Review it only if you do not recognize the activity.",
        "summary_zh": "账号出现新的登录活动；若不是本人操作，请立即检查安全记录。",
        "requires_action": True,
        "action": "Review the unfamiliar account sign-in",
        "evidence": "If you do not recognize this activity, review your account security immediately.",
    },
    {
        "trace_id": "public-demo-career-1", "sender": "careers@example.edu",
        "subject": "Graduate AI engineering opportunities",
        "intent": "EDUCATION_NOTICE", "category": "教育通知", "priority": "P2_NORMAL",
        "summary": "Three graduate AI engineering roles are open, with applications closing this month.",
        "summary_zh": "三个AI工程毕业生岗位正在招聘，申请将于本月底截止。",
        "requires_action": False,
    },
]


def seed():
    if db.stats()["total"]:
        return False
    base = datetime.now(timezone.utc)
    for index, item in enumerate(DEMO_EMAILS):
        deadline = base + timedelta(days=item.get("deadline_days", 0)) if item.get("deadline_days") else None
        received = (base - timedelta(hours=index * 5)).isoformat()
        record = {
            "trace_id": item["trace_id"], "message_id": f"<{item['trace_id']}@example.invalid>",
            "sender": item["sender"], "subject": item["subject"],
            "body_text": item["summary"] + "\n\n" + item.get("evidence", "For information only."),
            "date": received, "gmail_link": "", "threat_score": 0, "risk_level": "LOW",
            "is_safe": 1, "intent": item["intent"], "category": item["category"],
            "priority": item["priority"], "sentiment": "NEUTRAL", "language": "en-US",
            "summary": item["summary"], "summary_zh": item["summary_zh"], "context_json": "{}",
            "status": "已分类", "created_at": received, "account_id": "public-demo",
            "provider": "DEMO", "source_uid": str(index + 1), "internet_message_id": "",
            "provider_message_id": "", "received_at": received, "original_url": "",
            "content_hash": item["trace_id"], "uidvalidity": "demo", "provider_thread_id": "",
            "forwarded_by": "",
        }
        email_id = db.insert_email(record)
        action_items = []
        if item.get("action"):
            action_items.append({"title": item["action"], "evidence": item["evidence"],
                                 "deadline_at": deadline.isoformat() if deadline else None})
        analysis = {
            "intent": item["intent"], "priority": item["priority"], "confidence": .98,
            "requires_action": item["requires_action"], "requires_reply": False,
            "deadline_at": deadline.isoformat() if deadline else None,
            "deadline_text": "Public demonstration date" if deadline else None,
            "labels": ["synthetic-demo"], "entities": [], "reason_codes": ["DEMO_FIXTURE"],
            "model_provider": "fixture", "model_name": "", "prompt_version": "public-demo-v1",
            "action_items": action_items,
        }
        db.upsert_email_analysis(email_id, analysis)
        actions.sync(email_id, analysis)
        knowledge.index_email(db.get_email(email_id))
    topics.rebuild()
    return True
