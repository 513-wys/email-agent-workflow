"""Trusted provider links for opening a message in its original mailbox."""

from urllib.parse import quote


def gmail_message_url(account, provider_message_id):
    if not account or not provider_message_id:
        return ""
    try:
        message_hex = format(int(provider_message_id), "x")
    except (TypeError, ValueError):
        return ""
    return f"https://mail.google.com/mail/u/0/#all/{message_hex}"


def gmail_search_url(account, internet_message_id="", sender="", subject=""):
    if not account:
        return ""
    if internet_message_id and "@" in internet_message_id:
        query = f"rfc822msgid:{internet_message_id.strip()}"
    else:
        parts = []
        if sender:
            parts.append(f'from:"{sender.strip()}"')
        if subject:
            parts.append(f'subject:"{subject.strip()}"')
        query = " ".join(parts)
    if not query:
        return ""
    return f"https://mail.google.com/mail/u/0/#search/{quote(query, safe='')}"
