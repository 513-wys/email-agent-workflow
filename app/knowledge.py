"""Incremental local knowledge-document and chunk indexing."""
import hashlib
import json
import re

from app import db


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 140


def _content(email):
    return "\n".join(filter(None, (
        f"Subject: {email.get('subject', '')}",
        f"Sender: {email.get('sender') or email.get('from', '')}",
        f"Received: {email.get('received_at') or email.get('date', '')}",
        f"Summary: {email.get('summary_zh') or email.get('summary', '')}",
        email.get("body_text", ""),
    ))).strip()


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Create stable paragraph-aware chunks without losing long paragraphs."""
    cleaned = re.sub(r"\r\n?", "\n", text or "")
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", cleaned) if part.strip()]
    chunks, current = [], ""
    for paragraph in paragraphs:
        pieces = [paragraph[i:i + size] for i in range(0, len(paragraph), size)] or [paragraph]
        for piece in pieces:
            candidate = f"{current}\n\n{piece}".strip() if current else piece
            if current and len(candidate) > size:
                chunks.append(current)
                prefix = current[-overlap:] if overlap else ""
                current = f"{prefix}\n{piece}".strip()
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks


def index_email(email):
    if not email.get("is_safe") or email.get("status") != "已分类":
        return "ineligible", 0
    content = _content(email)
    if not content:
        return "empty", 0
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    chunks = chunk_text(content)
    metadata = {
        "email_id": email["id"], "sender": email.get("sender", ""),
        "received_at": email.get("received_at") or email.get("date", ""),
        "provider": email.get("provider", ""),
    }
    changed = db.replace_knowledge_document(
        source_type="EMAIL", source_id=str(email["id"]), title=email.get("subject") or "(No subject)",
        source_url=email.get("original_url") or "", content_hash=content_hash,
        chunks=[{
            "text": text, "token_count": max(1, len(text) // 4),
            "metadata_json": json.dumps(metadata, ensure_ascii=False),
        } for text in chunks],
    )
    return ("indexed" if changed else "unchanged"), len(chunks)


def index_all():
    counts = {"indexed": 0, "unchanged": 0, "ineligible": 0, "empty": 0, "chunks": 0}
    for email in db.list_emails(limit=10000):
        status, chunk_count = index_email(email)
        counts[status] += 1
        if status == "indexed":
            counts["chunks"] += chunk_count
    return counts
