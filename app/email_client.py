"""邮件接入：IMAP 拉取未读 + 演示模式（内置示例邮件）。"""
import imaplib
import email
import hashlib
import re
from datetime import datetime
from email.header import decode_header
from zoneinfo import ZoneInfo

from app import config, db, settings_store
from app.forwarded_mail import normalize
from app.mail_links import gmail_message_url


# 演示模式下的 4 条示例邮件（对应原测试用例 TC-01 ~ TC-04）
DEMO_EMAILS = [
    {
        "message_id": "demo-phish-001",
        "from": "billing@paypa1-security-alerts.net",
        "subject": "紧急：您的账户存在异常，请立即验证",
        "body_text": (
            "尊敬的客户，您的账户已被锁定。请点击 http://paypa1-security-alerts.net/verify "
            "输入您的密码与银行卡信息以恢复访问，否则账户将在 24 小时内注销。"
        ),
        "date": "2026-09-02 09:00",
        "headers": {"Authentication-Results": "spf=fail dkim=none dmarc=fail"},
    },
    {
        "message_id": "demo-biz-001",
        "from": "alice@partner-corp.com",
        "subject": "Q3 业务合作方案及报价咨询",
        "body_text": (
            "你好，我们希望探讨 Q3 季度在 AI 工作流自动化方面的合作，"
            "想了解你们的方案与报价，以及是否有相关案例可以参考。"
        ),
        "date": "2026-09-02 10:30",
        "headers": {"Authentication-Results": "spf=pass dkim=pass dmarc=pass"},
    },
    {
        "message_id": "demo-news-001",
        "from": "noreply@medium.com",
        "subject": "本周 AI 行业精选文章",
        "body_text": "本周为您精选了 5 篇 AI 行业深度文章，点击查看。",
        "date": "2026-09-02 08:00",
        "headers": {"Authentication-Results": "spf=pass dkim=pass dmarc=pass"},
    },
    {
        "message_id": "demo-en-001",
        "from": "bob@acme-global.com",
        "subject": "Request for pricing on AI automation solution",
        "body_text": (
            "Hi, we are evaluating AI workflow automation vendors for our ops team. "
            "Could you share your pricing and a reference case? Thanks."
        ),
        "date": "2026-09-02 11:00",
        "headers": {"Authentication-Results": "spf=pass dkim=pass dmarc=pass"},
    },
]


def _decode(s):
    if not s:
        return ""
    out = []
    for text, enc in decode_header(s):
        out.append(text.decode(enc or "utf-8", errors="replace") if isinstance(text, bytes) else text)
    return "".join(out)


def _decode_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            cd = str(part.get("Content-Disposition") or "")
            if part.get_content_type() == "text/plain" and "attachment" not in cd:
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return ""


def _norm(from_addr, subject, body, date, message_id, headers=None, gmail_link=None, **source):
    return {
        "message_id": message_id,
        "from": from_addr,
        "subject": subject,
        "body_text": body,
        "date": date,
        "headers": headers or {},
        "gmail_link": gmail_link or "",
        **source,
    }


def _account_id(provider, user):
    raw = f"{provider}:{(user or '').strip().lower()}".encode("utf-8")
    return "mail_" + hashlib.sha256(raw).hexdigest()[:16]


def _internaldate(meta):
    match = re.search(rb'INTERNALDATE "([^"]+)"', meta)
    if not match:
        return ""
    try:
        parsed = datetime.strptime(match.group(1).decode("ascii"), "%d-%b-%Y %H:%M:%S %z")
        return parsed.astimezone(ZoneInfo("Asia/Singapore")).isoformat()
    except (ValueError, UnicodeDecodeError):
        return ""


def _response_code(mail, name):
    code, values = mail.response(name)
    if code == name and values and values[0]:
        value = values[0]
        return value.decode() if isinstance(value, bytes) else str(value)
    return ""


def _demo_batch(limit):
    account_id = "mail_demo"
    state = db.get_sync_state(account_id) or {}
    last_uid = int(state.get("last_uid") or 0)
    emails = []
    for uid, item in enumerate(DEMO_EMAILS, start=1):
        if uid <= last_uid:
            continue
        emails.append(_norm(
            item["from"], item["subject"], item["body_text"], item["date"],
            item["message_id"], item.get("headers"),
            account_id=account_id,
            provider="DEMO",
            source_uid=str(uid),
            internet_message_id=item["message_id"],
            provider_message_id="",
            received_at=item["date"],
            uidvalidity="demo-v1",
        ))
    return {"account_id": account_id, "provider": "DEMO", "folder": "INBOX", "uidvalidity": "demo-v1", "emails": emails[:limit]}


def fetch_incremental(limit=100):
    """Fetch the newest unprocessed messages by stable IMAP UID without setting Seen."""
    mode = settings_store.get("mail_mode", "demo" if config.DEMO_MODE else "real")
    if mode == "demo":
        return _demo_batch(limit)

    provider = settings_store.get("mail_provider", "gmail")
    preset = settings_store.PROVIDERS.get(provider, settings_store.PROVIDERS["gmail"])
    user = settings_store.get("mail_user", config.IMAP_USER)
    password = settings_store.get("mail_password", config.IMAP_PASSWORD)
    if not user or not password:
        raise RuntimeError("未配置邮箱账号：请在「设置」页填写邮箱地址和应用专用密码/授权码，或切回演示模式")

    account_id = _account_id(provider, user)
    folder = "INBOX"
    mail = imaplib.IMAP4_SSL(preset["host"], preset["port"])
    try:
        mail.login(user, password)
        status, _ = mail.select(folder, readonly=True)
        if status != "OK":
            raise RuntimeError("无法以只读方式打开收件箱")

        uidvalidity = _response_code(mail, "UIDVALIDITY")
        state = db.get_sync_state(account_id, folder) or {}
        saved_validity = state.get("uidvalidity") or ""
        last_uid = int(state.get("last_uid") or 0) if not saved_validity or saved_validity == uidvalidity else 0
        start_uid = last_uid + 1
        status, data = mail.uid("search", None, "UID", f"{start_uid}:*")
        if status != "OK":
            raise RuntimeError("邮箱增量检索失败")
        all_ids = [uid for uid in (data[0].split() if data and data[0] else []) if int(uid) > last_uid]
        # A bounded first sync should establish a useful recent baseline, not spend
        # the allowance on the oldest messages in a large mailbox. Advancing the
        # cursor to the newest selected UID makes later runs truly incremental.
        ids = all_ids[-limit:]
        results = []
        for uid in ids:
            status, msg_data = mail.uid(
                "fetch", uid, "(UID INTERNALDATE X-GM-MSGID X-GM-THRID BODY.PEEK[])"
            )
            if status != "OK" or not msg_data:
                raise RuntimeError(f"邮件 UID {uid.decode()} 拉取失败")
            pair = next((item for item in msg_data if isinstance(item, tuple) and len(item) == 2), None)
            if not pair:
                raise RuntimeError(f"邮件 UID {uid.decode()} 返回格式异常")
            meta, raw = pair
            msg = email.message_from_bytes(raw)
            gm_match = re.search(rb"X-GM-MSGID\s+(\d+)", meta)
            provider_message_id = gm_match.group(1).decode() if gm_match else ""
            thread_match = re.search(rb"X-GM-THRID\s+(\d+)", meta)
            provider_thread_id = thread_match.group(1).decode() if thread_match else ""
            gmail_link = gmail_message_url(user, provider_thread_id or provider_message_id) if provider == "gmail" else ""
            received_at = _internaldate(meta)
            internet_message_id = (msg.get("Message-ID") or "").strip()
            normalized = _norm(
                _decode(msg.get("From", "")),
                _decode(msg.get("Subject", "")),
                _decode_body(msg),
                received_at or msg.get("Date", ""),
                internet_message_id or uid.decode(),
                dict(msg.items()),
                gmail_link=gmail_link,
                account_id=account_id,
                provider=provider.upper(),
                source_uid=uid.decode(),
                internet_message_id=internet_message_id,
                provider_message_id=provider_message_id,
                provider_thread_id=provider_thread_id,
                received_at=received_at,
                uidvalidity=uidvalidity,
            )
            owner_emails = settings_store.get("owner_emails", user) or user
            results.append(normalize(normalized, owner_emails))
        return {
            "account_id": account_id, "provider": provider.upper(), "folder": folder,
            "uidvalidity": uidvalidity, "emails": results,
            "remaining": 0,
            "older_skipped": max(0, len(all_ids) - len(ids)),
        }
    finally:
        try:
            mail.logout()
        except Exception:
            pass


def fetch_unread(limit=100):
    """Compatibility wrapper returning only the incremental message list."""
    return fetch_incremental(limit)["emails"]
