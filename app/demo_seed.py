"""Seed the public sandbox from the canonical 20-message synthetic dataset."""
from __future__ import annotations

import json
from pathlib import Path

from app import actions, db, knowledge, topics


DATASET_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "demo_email_cases.json"

CATEGORY_CODES = {
    "Education notice": "EDUCATION_NOTICE", "Project update": "PROJECT_UPDATE",
    "Action required": "ACTION_REQUIRED", "Security alert": "SECURITY_ALERT",
    "Security interception": "SECURITY_ALERT", "Payment and billing": "PAYMENT_BILLING",
    "Newsletter": "NEWSLETTER", "Meeting and calendar": "MEETING_CALENDAR",
    "Customer support": "CUSTOMER_SUPPORT", "Personal": "PERSONAL",
}


def _entities(case):
    topic = case["expected"].get("topic") or ""
    if topic.startswith("course:"):
        return [{"type": "COURSE", "value": topic.split(":", 1)[1]}]
    if topic.startswith("project:"):
        return [{"type": "PROJECT", "value": f"Project {topic.split(':', 1)[1]}"}]
    if topic.startswith("subscription:"):
        return [{"type": "ORGANIZATION", "value": topic.split(":", 1)[1]}]
    return []


def _analysis(case):
    expected = case["expected"]
    action_title = expected.get("action") or expected.get("conditional_action")
    action_items = []
    if action_title:
        action_items.append({
            "title": action_title, "evidence": case["body"],
            "deadline_at": expected.get("deadline"),
        })
    return {
        "intent": expected["intent"], "priority": expected["priority"], "confidence": 0.98,
        "requires_action": expected.get("requires_action", False), "requires_reply": False,
        "deadline_at": expected.get("deadline"), "deadline_text": None,
        "labels": [expected["topic"]] if expected.get("topic") else [],
        "entities": _entities(case), "reason_codes": ["SYNTHETIC_DEMO_FIXTURE"],
        "model_provider": "fixture", "model_name": "", "prompt_version": "public-demo-v3",
        "action_items": action_items,
    }


def _record(case, index):
    expected = case["expected"]
    safe = expected.get("safe", True)
    return {
        "trace_id": case["id"], "message_id": f"<{case['id']}@example.invalid>",
        "sender": case["sender"], "subject": case["subject"], "body_text": case["body"],
        "date": case["received_at"], "gmail_link": "", "threat_score": 95 if not safe else 0,
        "risk_level": "CRITICAL" if not safe else "LOW", "is_safe": int(safe),
        "intent": expected["intent"], "category": CATEGORY_CODES[expected["category"]],
        "priority": expected["priority"], "sentiment": "NEUTRAL", "language": "en-US",
        "summary": case.get("summary", case["body"]), "summary_zh": "",
        "context_json": json.dumps({"synthetic": True, "case_id": case["id"]}),
        "status": "已分类" if safe else "已隔离", "created_at": case["received_at"],
        "account_id": case["account"], "provider": "DEMO", "source_uid": str(index),
        "internet_message_id": "", "provider_message_id": case["id"],
        "received_at": case["received_at"], "original_url": "", "content_hash": case["id"],
        "uidvalidity": "public-demo-v3", "provider_thread_id": case["id"],
        "forwarded_by": "demo.student@example.com" if case["source"] == "university_forwarded" else "",
    }


def seed():
    """Load the canonical fixture once; public demo databases contain no real mail."""
    if db.public_demo_dataset_is_current():
        return False
    if db.stats()["total"]:
        db.reset_public_demo_data()
    cases = json.loads(DATASET_PATH.read_text())["cases"]
    for index, case in enumerate(cases, 1):
        record = _record(case, index)
        analysis = _analysis(case)
        email_id = db.insert_email(record)
        db.upsert_email_analysis(email_id, analysis)
        if record["is_safe"]:
            actions.sync(email_id, analysis)
            knowledge.index_email(db.get_email(email_id))
    topics.rebuild()
    return True
