"""Deterministic action-item generation from validated email analysis."""
import hashlib
import re
from datetime import datetime

from app import db, topics


def _fingerprint(title):
    normalized = re.sub(r"\s+", " ", (title or "").strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]


def sync(email_id, analysis):
    """Upsert system-generated actions without overwriting user decisions."""
    email = db.get_email(email_id) or {}
    if topics.is_subscription(email, analysis):
        db.dismiss_stale_actions(email_id, [])
        return 0
    candidates = analysis.get("action_items") or []
    if not analysis.get("requires_action") and analysis.get("intent") != "VERIFICATION_CODE":
        candidates = []
    active = []
    for item in candidates:
        title = str(item.get("title") or "").strip()
        evidence = str(item.get("evidence") or "").strip()
        if not title or not evidence:
            continue
        fingerprint = _fingerprint(title)
        deadline = item.get("deadline_at") or analysis.get("deadline_at")
        expiry = deadline if analysis.get("intent") == "VERIFICATION_CODE" else None
        db.upsert_action_item({
            "email_id": email_id, "fingerprint": fingerprint, "title": title,
            "details": analysis.get("deadline_text") or "", "priority": analysis.get("priority") or "P2_NORMAL",
            "deadline_at": deadline, "expiry_at": expiry, "evidence_text": evidence,
            "now": datetime.now().astimezone().isoformat(),
        })
        active.append(fingerprint)
    db.dismiss_stale_actions(email_id, active)
    return len(active)
