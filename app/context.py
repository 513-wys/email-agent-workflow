"""上下文富化（对应 n8n 子流 03）：CRM 客户画像 + 官网抓取总结 + 知识库（v1 预留）。"""
import re

import requests

from app import db, llm


def _lookup_crm(from_addr):
    c = db.get_contact(from_addr)
    if c:
        return {
            "crm_contact_found": True,
            "client_name": c["name"],
            "client_tier": c["tier"],
            "deal_stage": c["deal_stage"],
        }
    return {"crm_contact_found": False, "client_name": "", "client_tier": "", "deal_stage": ""}


def _scrape_website(from_addr):
    domain = (from_addr or "").split("@")[-1]
    if not domain or "." not in domain:
        return ""
    try:
        r = requests.get(f"https://{domain}", timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text).strip()[:3000]
        if len(text) < 40:
            return ""
        summary = llm.chat_text(
            "用 2-3 句简体中文概括这家公司的业务模式。若文本为空或为错误页面，仅输出 [无有效信息]。",
            text, max_tokens=200,
        )
        return (summary or "").strip()
    except Exception:
        return ""


def enrich(email, triage):
    """返回 context 字典。"""
    crm = _lookup_crm(email.get("from", ""))
    web = _scrape_website(email.get("from", ""))
    return {
        "crm_contact_found": crm["crm_contact_found"],
        "client_name": crm["client_name"],
        "client_tier": crm["client_tier"],
        "deal_stage": crm["deal_stage"],
        "kb_references": [],  # v1 暂不做向量检索，预留字段
        "web_scraped_summary": web,
    }
