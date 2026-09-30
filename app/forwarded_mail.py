"""Identify the original sender inside user-owned forwarded messages."""
import re
from email.utils import parseaddr


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
FORWARDED_FROM_RE = re.compile(
    r"(?im)^\s*(?:发件人|寄件者|from)\s*[:：]\s*(.+?)\s*$"
)


def parse_owner_emails(value):
    if isinstance(value, (list, tuple, set)):
        parts = value
    else:
        parts = re.split(r"[,;\s]+", value or "")
    return sorted({p.strip().lower() for p in parts if EMAIL_RE.fullmatch(p.strip())})


def address_of(value):
    parsed = parseaddr(value or "")[1]
    if parsed:
        return parsed.lower()
    match = EMAIL_RE.search(value or "")
    return match.group(0).lower() if match else ""


def original_sender(wrapper_sender, body_text, owner_emails):
    """Return original forwarded sender only when the wrapper belongs to the user."""
    owners = set(parse_owner_emails(owner_emails))
    if address_of(wrapper_sender) not in owners:
        return ""
    for match in FORWARDED_FROM_RE.finditer(body_text or ""):
        candidate = match.group(1).strip()
        candidate_address = address_of(candidate)
        if candidate_address and candidate_address not in owners:
            return candidate
    return ""


def normalize(message, owner_emails):
    wrapper = message.get("from", "")
    original = original_sender(wrapper, message.get("body_text", ""), owner_emails)
    if original:
        message["forwarded_by"] = wrapper
        message["from"] = original
        message["is_forwarded"] = True
    else:
        message["forwarded_by"] = ""
        message["is_forwarded"] = False
    return message
