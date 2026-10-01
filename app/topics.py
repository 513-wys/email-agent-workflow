"""Deterministic cross-email topic organization built from stored analysis."""
import json
import re
from datetime import datetime

from app import db


def _text(email, analysis):
    return " ".join(str(value or "") for value in (
        email.get("subject"), email.get("summary"), email.get("summary_zh"),
        analysis.get("labels_json"), analysis.get("entities_json"),
    )).lower()


def _entity(analysis, kinds):
    try:
        entities = json.loads(analysis.get("entities_json") or "[]")
    except (TypeError, ValueError):
        entities = []
    for item in entities:
        if item.get("type") in kinds and str(item.get("value") or "").strip():
            return str(item["value"]).strip()
    return ""


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def _subscription_organization(email, analysis):
    entity = _entity(analysis, {"ORGANIZATION", "PROJECT"})
    if entity:
        return entity
    subject = str(email.get("subject") or "").strip()
    match = re.match(
        r"([A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){0,2})\s+"
        r"(?:annual\s+plan|pro\b|renewal\b|payment\b|card\b|plan\b|now\b)",
        subject,
    )
    if match:
        return match.group(1).strip()
    sender = str(email.get("sender") or "")
    domain = sender.rsplit("@", 1)[-1].split(".", 1)[0]
    return domain.replace("-", " ").title() if domain and domain != sender else "Subscriptions"


def classify(email, analysis):
    """Return a stable topic key, type, and bilingual title."""
    text = _text(email, analysis)
    intent = email.get("intent") or "OTHER"
    if intent == "PERSONAL":
        sender = str(email.get("sender") or "").lower()
        local_part = sender.split("@", 1)[0]
        correspondent = re.sub(r"[^a-z0-9]+", "-", local_part).strip("-") or "correspondence"
        return f"personal:{correspondent}", "PERSONAL", "Personal correspondence", "个人邮件"
    support_case = re.search(r"\b(CS-\d{4,})\b", text, re.I)
    if support_case:
        case_id = support_case.group(1).upper()
        return f"support:{case_id}", "SUPPORT", f"Support case {case_id}", f"支持工单 {case_id}"
    subject = str(email.get("subject") or "")
    project = re.search(r"\bProject\s+([A-Z][A-Za-z0-9-]{1,30})\b", subject)
    if project:
        name = project.group(1).upper()
        return f"project:{name}", "PROJECT", f"Project {name}", f"Project {name} 项目"
    course = re.search(r"\b([A-Z]{2,4}\d{4})\b", text, re.I)
    if course:
        code = course.group(1).upper()
        return f"course:{code}", "COURSE", f"{code} course updates", f"{code} 课程动态"
    if any(word in text for word in ("showmeyouragent", "show me your agent", "smya hackathon", "questbond")):
        return "project:showmeyouragent", "PROJECT", "ShowMeYourAgent hackathon", "ShowMeYourAgent 黑客松"
    if intent == "MEETING_CALENDAR":
        subject = str(email.get("subject") or "")
        subject = subject.rsplit(":", 1)[-1].strip()
        event = re.search(
            r"(?:invitation:\s*)?([A-Za-z][A-Za-z0-9&'-]*(?:\s+[A-Za-z][A-Za-z0-9&'-]*){0,4}\s+"
            r"(?:roundtable|seminar|workshop|webinar|conference))\b",
            subject,
            re.I,
        )
        if event:
            title = event.group(1).strip()
            key = _slug(title)
            return f"event:{key}", "EVENT", title, f"{title} 活动"
    if any(word in text for word in ("subscription", "renew", "billing cycle", "trial", "订阅", "续订", "试用期")):
        if "google one" in text:
            organization = "Google One"
        elif "chatgpt" in text or "openai" in text:
            organization = "ChatGPT Plus"
        else:
            organization = _subscription_organization(email, analysis)
        key = organization if organization != "Subscriptions" else "general"
        return f"subscription:{key}", "SUBSCRIPTION", f"{organization} subscription", f"{organization} 订阅"
    if email.get("intent") == "NEWSLETTER":
        organization = _subscription_organization(email, analysis)
        key = organization if organization != "Subscriptions" else "general"
        return f"subscription:{key}", "SUBSCRIPTION", f"{organization} updates", f"{organization} 资讯订阅"
    if (email.get("intent") == "SECURITY_ALERT"):
        if "google" in text:
            return "security:google", "SECURITY", "Google account security", "Google 账号安全"
        return "security:account", "SECURITY", "Account and mailbox security", "账号与邮箱安全"
    if any(word in text for word in ("recruitment", "career", "job", "internship", "招聘", "实习", "职位")):
        return "career:opportunities", "CAREER", "Career and recruitment opportunities", "求职与招聘机会"
    if any(word in text for word in ("election", "voting", "vote", "选举", "投票")):
        return "campus:elections", "CAMPUS", "Campus elections", "校园选举"
    aliases = {
        "NEWSLETTER_OR_INFO": "NEWSLETTER", "TRANSACTIONAL": "OTHER",
        "SECURITY_OR_VERIFICATION": "SECURITY_ALERT", "INTERNAL_COLLABORATION": "PROJECT_UPDATE",
        "SPAM_OR_COLD": "MARKETING",
    }
    intent = aliases.get(intent, intent)
    labels = {
        "MEETING_CALENDAR": ("Events and meetings", "活动与会议", "EVENT"),
        "EDUCATION_NOTICE": ("Learning and campus notices", "学习与校园通知", "EDUCATION"),
        "NEWSLETTER": ("Newsletters and updates", "资讯订阅与动态", "SUBSCRIPTION"),
        "MARKETING": ("Product news and promotions", "产品资讯与推广", "SUBSCRIPTION"),
        "PAYMENT_BILLING": ("Payments and bills", "付款与账单", "BILLING"),
        "PROJECT_UPDATE": ("Project updates", "项目动态", "PROJECT"),
        "ACTION_REQUIRED": ("Other matters requiring action", "其他待处理事项", "ACTION"),
        "BUSINESS_INQUIRY": ("Business inquiries", "商务合作", "BUSINESS"),
        "CUSTOMER_SUPPORT": ("Customer support", "客户支持", "SUPPORT"),
        "PERSONAL": ("Personal correspondence", "个人邮件", "PERSONAL"),
        "VERIFICATION_CODE": ("Verification messages", "验证码通知", "SECURITY"),
        "SECURITY_ALERT": ("Account and mailbox security", "账号与邮箱安全", "SECURITY"),
    }
    en, zh, kind = labels.get(intent, ("Other email updates", "其他邮件动态", "OTHER"))
    return f"category:{intent.lower()}", kind, en, zh


def is_subscription(email, analysis):
    return classify(email, analysis)[1] == "SUBSCRIPTION"


def rebuild():
    rows = db.list_emails_with_analysis()
    topics = {}
    for email in rows:
        if not email.get("is_safe") or email.get("status") != "已分类":
            continue
        key, kind, title_en, title_zh = classify(email, email)
        item = topics.setdefault(key, {
            "topic_key": key, "topic_type": kind, "title_en": title_en, "title_zh": title_zh,
            "email_ids": [], "summary_en": "", "summary_zh": "", "latest_update_at": "", "deadline_at": None,
        })
        item["email_ids"].append(email["id"])
        received = email.get("received_at") or email.get("date") or ""
        if received >= item["latest_update_at"]:
            item["latest_update_at"] = received
            item["summary_en"] = email.get("summary") or email.get("subject") or ""
            item["summary_zh"] = email.get("summary_zh") or email.get("summary") or email.get("subject") or ""
        deadline = email.get("deadline_at")
        if deadline and (not item["deadline_at"] or deadline > item["deadline_at"]):
            item["deadline_at"] = deadline
    db.replace_topics(list(topics.values()), datetime.now().astimezone().isoformat())
    return len(topics)
