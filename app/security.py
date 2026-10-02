"""Apply deterministic link, sender, and content risk signals before triage."""
import re

from app import llm, settings_store
from app.forwarded_mail import address_of, parse_owner_emails

WHITELIST_DOMAINS = [
    "google.com", "github.com", "microsoft.com", "outlook.com", "gmail.com",
    "notion.so", "slack.com", "telegram.org", "t.me", "zoom.us", "calendly.com",
    "ntu.edu.sg", "e.ntu.edu.sg",
]

SECURITY_PROMPT = (
    "You are an expert Cybersecurity AI Mail Filter. Analyze the incoming email for phishing "
    "indicators, social engineering, impersonation, credential harvesting, malicious links, or "
    "BEC (fake invoice / payment-redirect) patterns.\n\n"
    "Review the pre-extracted URL scan: 'urls' is the full link list, 'risky_urls' are links whose "
    "domain is NOT whitelisted. A non-whitelisted URL requires review but is not, by itself, proof "
    "of phishing. Forwarding is not impersonation: when original sender information was extracted "
    "from a user-owned forwarding account, judge the original sender and content, and do not treat "
    "the forwarding wrapper as suspicious. Institutional announcements may legitimately link to an "
    "external voting, survey, event, or recruitment service. Quarantine only with concrete evidence "
    "of credential theft, payment redirection, secret-code collection, malware, or clear deception.\n\n"
    "Respond with STRICTLY valid JSON only (no markdown fences):\n"
    '{"is_safe": boolean, "threat_score": number(0-100), "risk_level": "LOW"|"MEDIUM"|"HIGH"|"CRITICAL", "reasons": string[]}\n\n'
    "Rules: threat_score >= 75 => is_safe must be false. No real risk => is_safe true, reasons []. "
    "Base judgment ONLY on provided evidence."
)


def _host_of(url):
    m = re.match(r"^https?://([^/?#]+)", url, re.IGNORECASE)
    return m.group(1).replace("www.", "").lower() if m else ""


def _is_whitelisted(host):
    return any(host == d or host.endswith("." + d) for d in WHITELIST_DOMAINS)


def _scan(email):
    text = (email.get("body_text") or "") + " " + (email.get("body_html") or "")
    urls = list(set(re.findall(r"https?://[^\s\"'<>)\]]+", text, re.IGNORECASE)))
    urls = [u.rstrip(".,;!?") for u in urls]
    risky = [u for u in urls if not _is_whitelisted(_host_of(u))]
    headers = email.get("headers") or {}
    auth = {
        "spf": headers.get("Received-SPF") or headers.get("Authentication-Results") or "unknown",
        "dkim": "present" if "DKIM-Signature" in headers else ("check" if "Authentication-Results" in headers else "unknown"),
        "dmarc": headers.get("Authentication-Results") or "unknown",
    }
    return urls, risky, auth


def _trusted_forward(email):
    if not email.get("forwarded_by"):
        return False
    sender_domain = address_of(email.get("from", "")).split("@")[-1]
    owner_domains = {address.split("@")[-1] for address in parse_owner_emails(
        settings_store.get("owner_emails", "")
    )}
    return bool(sender_domain) and any(
        sender_domain == domain or sender_domain.endswith("." + domain) or domain.endswith("." + sender_domain)
        for domain in owner_domains
    )


def _has_decisive_harm(email):
    text = " ".join((email.get("subject", ""), email.get("body_text", ""))).lower()
    patterns = (
        r"\bpassword\b", r"\botp\b", r"one[- ]time (?:password|code)",
        r"bank account", r"credit card", r"wire transfer", r"gift card",
        r"recovery phrase", r"seed phrase", r"install (?:this )?(?:file|attachment)",
        r"银行卡", r"验证码", r"转账", r"密码",
    )
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def evaluate(email):
    """返回 security_assessment 字典。"""
    urls, risky, auth = _scan(email)
    user = (
        f"From: {email.get('from', '')}\nForwarded by user account: {email.get('forwarded_by', '')}\n"
        f"Subject: {email.get('subject', '')}\nDate: {email.get('date', '')}\n\n"
        f"--- 邮件正文 ---\n{(email.get('body_text') or '')[:4000]}\n\n"
        f"--- 外链扫描 ---\n全部链接: {urls}\n非白名单链接: {risky}\n发件认证: {auth}"
    )
    ai = llm.chat_json(SECURITY_PROMPT, user, temperature=0.1, max_tokens=400)

    threat_score = int(ai.get("threat_score", 0) or 0)
    reasons = list(ai.get("reasons") or [])
    if risky:
        threat_score = max(threat_score, 40)
        reasons.append(f"存在 {len(risky)} 个非白名单外链")
    if _trusted_forward(email) and not _has_decisive_harm(email) and threat_score >= 75:
        threat_score = 70
        reasons.append("原始发件人与用户所属机构域一致；转发本身不作为隔离依据")
    is_safe = threat_score < 75 and ai.get("is_safe") is not False
    if threat_score < 75:
        is_safe = True
    risk_level = (
        "CRITICAL" if threat_score >= 90 else "HIGH" if threat_score >= 50
        else "MEDIUM" if threat_score >= 25 else "LOW"
    )
    return {
        "is_safe": is_safe,
        "threat_score": threat_score,
        "risk_level": risk_level,
        "detected_risks": reasons,
    }
