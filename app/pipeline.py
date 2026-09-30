"""主流水线（对应 n8n 主调度器 00）：安全 → 分类 → 富化 → 落库。"""
import hashlib
import json

from app import actions, db, email_client, knowledge, security, topics, triage, context


def _trace_id(email):
    key = ":".join(filter(None, (
        email.get("account_id", ""),
        email.get("uidvalidity", ""),
        email.get("source_uid", ""),
        email.get("internet_message_id", ""),
    ))) or email.get("message_id") or email.get("subject") or email.get("from") or "unknown"
    return "email_" + hashlib.md5(key.encode("utf-8")).hexdigest()[:12]


def _base_record(email, trace_id):
    content = "\n".join((email.get("from", ""), email.get("subject", ""), email.get("body_text", "")))
    return {
        "trace_id": trace_id,
        "message_id": email.get("message_id", ""),
        "sender": email.get("from", ""),
        "subject": email.get("subject", ""),
        "body_text": (email.get("body_text") or "")[:4000],
        "date": email.get("date", ""),
        "gmail_link": email.get("gmail_link", ""),
        "threat_score": 0,
        "risk_level": "",
        "is_safe": 1,
        "intent": "",
        "category": "",
        "priority": "",
        "sentiment": "",
        "language": "",
        "summary": "",
        "summary_zh": "",
        "context_json": "{}",
        "status": "",
        "created_at": db.now_str(),
        "account_id": email.get("account_id"),
        "provider": email.get("provider"),
        "source_uid": email.get("source_uid"),
        "internet_message_id": email.get("internet_message_id"),
        "provider_message_id": email.get("provider_message_id"),
        "provider_thread_id": email.get("provider_thread_id"),
        "forwarded_by": email.get("forwarded_by", ""),
        "received_at": email.get("received_at"),
        "original_url": email.get("gmail_link", ""),
        "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "uidvalidity": email.get("uidvalidity"),
    }


def process_one(email):
    """处理单封邮件，返回落库后的记录 dict。"""
    trace_id = _trace_id(email)
    rec = _base_record(email, trace_id)

    # 01 安全网关
    sec = security.evaluate(email)
    rec.update({
        "threat_score": sec["threat_score"],
        "risk_level": sec["risk_level"],
        "is_safe": 1 if sec["is_safe"] else 0,
    })
    if not sec["is_safe"]:
        rec["category"] = "安全拦截"
        rec["status"] = "已隔离"
        rec["summary"] = "威胁评分 " + str(sec["threat_score"]) + "（" + (sec["risk_level"] or "") + "）"
        rec["summary_zh"] = "；".join(sec["detected_risks"]) or "高危邮件"
        db.insert_email(rec)
        return rec

    # 02 意图分类
    tri = triage.classify(email)
    rec.update({
        "intent": tri["intent"],
        "category": tri["category"],
        "priority": tri["priority"],
        "sentiment": tri["sentiment"],
        "language": tri["language"],
        "summary": tri["summary"],
        "summary_zh": tri["summary_zh"],
    })

    # 03 上下文富化
    ctx = context.enrich(email, tri)
    rec["context_json"] = json.dumps(ctx, ensure_ascii=False)
    rec["status"] = "已分类"
    email_id = db.insert_email(rec)
    db.upsert_email_analysis(email_id, tri)
    actions.sync(email_id, tri)
    indexed_email = db.get_email(email_id)
    if indexed_email:
        knowledge.index_email(indexed_email)
        topics.rebuild()
    return rec


def ingest(limit=100, progress_callback=None):
    """拉取未读邮件并逐封处理，返回结果列表。"""
    if progress_callback:
        progress_callback({"phase": "fetching"})
    batch = email_client.fetch_incremental(limit)
    emails = batch["emails"]
    if progress_callback:
        progress_callback({"phase": "processing", "total": len(emails), "processed": 0})
    results = []
    skipped = 0
    last_persisted_uid = None
    for index, e in enumerate(emails, start=1):
        if db.email_exists_by_source(e.get("account_id"), e.get("uidvalidity"), e.get("source_uid")):
            skipped += 1
            last_persisted_uid = e.get("source_uid")
            if progress_callback:
                progress_callback({"processed": index, "skipped": skipped})
            continue
        try:
            results.append(process_one(e))
        except Exception as ex:  # 处理失败（如未配大模型）也落一条记录，不中断
            trace_id = _trace_id(e)
            rec = _base_record(e, trace_id)
            rec["status"] = "处理失败"
            rec["summary"] = str(ex)[:200]
            rec["summary_zh"] = str(ex)[:200]
            try:
                db.insert_email(rec)
            except Exception:
                break
            results.append(rec)
        last_persisted_uid = e.get("source_uid")
        if progress_callback:
            failed_so_far = sum(1 for item in results if item.get("status") == "处理失败")
            progress_callback({
                "processed": index,
                "inserted": len(results) - failed_so_far,
                "failed": failed_so_far,
                "skipped": skipped,
            })
    if last_persisted_uid is not None:
        db.update_sync_state(
            batch["account_id"], batch["folder"], batch["uidvalidity"], last_persisted_uid
        )
    failed = sum(1 for item in results if item.get("status") == "处理失败")
    return {
        "results": results,
        "inserted": len(results) - failed,
        "skipped": skipped,
        "failed": failed,
        "remaining": batch.get("remaining", 0),
        "older_skipped": batch.get("older_skipped", 0),
    }
