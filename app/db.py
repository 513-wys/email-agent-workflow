"""SQLite 存储：审计日志（emails 表）+ CRM 客户表（contacts 表）。"""
import json
import sqlite3
from datetime import datetime

from app import tenant
from app.migrations import apply_migrations
from app.forwarded_mail import normalize


def _conn():
    conn = sqlite3.connect(tenant.db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = _conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT UNIQUE,
            message_id TEXT,
            sender TEXT,
            subject TEXT,
            body_text TEXT,
            date TEXT,
            gmail_link TEXT DEFAULT '',
            threat_score INTEGER,
            risk_level TEXT,
            is_safe INTEGER,
            intent TEXT,
            category TEXT,
            priority TEXT,
            sentiment TEXT,
            language TEXT,
            summary TEXT,
            summary_zh TEXT,
            context_json TEXT,
            status TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            name TEXT,
            tier TEXT,
            deal_stage TEXT
        );
        """
    )
    conn.commit()
    # 演示用 CRM 种子数据
    if conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO contacts(email,name,tier,deal_stage) VALUES(?,?,?,?)",
            [
                ("alice@partner-corp.com", "王女士", "VIP企业", "谈判中"),
                ("bob@acme-global.com", "Bob Chen", "普通客户", "接洽中"),
            ],
        )
        conn.commit()
    apply_migrations(conn)
    conn.close()


def insert_email(record: dict):
    record = {**record, "forwarded_by": record.get("forwarded_by", "")}
    conn = _conn()
    conn.execute(
        """
        INSERT INTO emails
        (trace_id, message_id, sender, subject, body_text, date, gmail_link, threat_score, risk_level, is_safe,
         intent, category, priority, sentiment, language, summary, summary_zh, context_json, status, created_at,
         account_id, provider, source_uid, internet_message_id, provider_message_id, received_at, original_url,
         content_hash, uidvalidity, provider_thread_id, forwarded_by)
        VALUES
        (:trace_id, :message_id, :sender, :subject, :body_text, :date, :gmail_link, :threat_score, :risk_level, :is_safe,
         :intent, :category, :priority, :sentiment, :language, :summary, :summary_zh, :context_json, :status, :created_at,
         :account_id, :provider, :source_uid, :internet_message_id, :provider_message_id, :received_at, :original_url,
         :content_hash, :uidvalidity, :provider_thread_id, :forwarded_by)
        ON CONFLICT(trace_id) DO UPDATE SET
            sender=excluded.sender,
            subject=excluded.subject,
            body_text=excluded.body_text,
            date=excluded.date,
            gmail_link=excluded.gmail_link,
            threat_score=excluded.threat_score,
            risk_level=excluded.risk_level,
            is_safe=excluded.is_safe,
            intent=excluded.intent,
            category=excluded.category,
            priority=excluded.priority,
            sentiment=excluded.sentiment,
            language=excluded.language,
            summary=excluded.summary,
            summary_zh=excluded.summary_zh,
            context_json=excluded.context_json,
            status=excluded.status,
            account_id=COALESCE(excluded.account_id, emails.account_id),
            provider=COALESCE(excluded.provider, emails.provider),
            source_uid=COALESCE(excluded.source_uid, emails.source_uid),
            internet_message_id=COALESCE(excluded.internet_message_id, emails.internet_message_id),
            provider_message_id=COALESCE(excluded.provider_message_id, emails.provider_message_id),
            received_at=COALESCE(excluded.received_at, emails.received_at),
            original_url=COALESCE(excluded.original_url, emails.original_url),
            content_hash=COALESCE(excluded.content_hash, emails.content_hash),
            uidvalidity=COALESCE(excluded.uidvalidity, emails.uidvalidity),
            provider_thread_id=COALESCE(excluded.provider_thread_id, emails.provider_thread_id),
            forwarded_by=COALESCE(excluded.forwarded_by, emails.forwarded_by)
        """,
        record,
    )
    conn.commit()
    email_id = conn.execute(
        "SELECT id FROM emails WHERE trace_id=?", (record["trace_id"],)
    ).fetchone()[0]
    conn.close()
    return email_id


def get_sync_state(account_id, folder="INBOX"):
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM mail_sync_state WHERE account_id=? AND folder=?",
        (account_id, folder),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_email_analysis(email_id, result):
    now = datetime.now().astimezone().isoformat()
    conn = _conn()
    conn.execute(
        """
        INSERT INTO email_analysis
        (email_id, category, priority, confidence, requires_action, requires_reply,
         deadline_at, deadline_text, labels_json, entities_json, reason_codes_json,
         model_provider, model_name, prompt_version, created_at, updated_at, action_items_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email_id) DO UPDATE SET
          category=excluded.category, priority=excluded.priority, confidence=excluded.confidence,
          requires_action=excluded.requires_action, requires_reply=excluded.requires_reply,
          deadline_at=excluded.deadline_at, deadline_text=excluded.deadline_text,
          labels_json=excluded.labels_json, entities_json=excluded.entities_json,
          reason_codes_json=excluded.reason_codes_json, model_provider=excluded.model_provider,
          model_name=excluded.model_name, prompt_version=excluded.prompt_version,
          updated_at=excluded.updated_at, action_items_json=excluded.action_items_json
        """,
        (email_id, result["intent"], result["priority"], result["confidence"],
         int(result["requires_action"]), int(result["requires_reply"]), result["deadline_at"],
         result["deadline_text"], json.dumps(result["labels"], ensure_ascii=False),
         json.dumps(result["entities"], ensure_ascii=False), json.dumps(result["reason_codes"], ensure_ascii=False),
         result["model_provider"], result["model_name"], result["prompt_version"], now, now,
         json.dumps(result["action_items"], ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def get_email_analysis(email_id):
    conn = _conn()
    row = conn.execute("SELECT * FROM email_analysis WHERE email_id=?", (email_id,)).fetchone()
    conn.close()
    if not row:
        return None
    result = dict(row)
    for source, target in (("labels_json", "labels"), ("entities_json", "entities"),
                           ("reason_codes_json", "reason_codes"), ("action_items_json", "action_items")):
        result[target] = json.loads(result.get(source) or "[]")
    return result


def upsert_action_item(item):
    conn = _conn()
    conn.execute(
        """
        INSERT INTO action_items
        (email_id, fingerprint, title, details, status, priority, deadline_at, expiry_at,
         evidence_text, created_at, updated_at, user_modified)
        VALUES (:email_id, :fingerprint, :title, :details, 'OPEN', :priority,
                :deadline_at, :expiry_at, :evidence_text, :now, :now, 0)
        ON CONFLICT(email_id, fingerprint) DO UPDATE SET
          title=CASE WHEN action_items.user_modified=0 THEN excluded.title ELSE action_items.title END,
          details=CASE WHEN action_items.user_modified=0 THEN excluded.details ELSE action_items.details END,
          priority=CASE WHEN action_items.user_modified=0 THEN excluded.priority ELSE action_items.priority END,
          deadline_at=CASE WHEN action_items.user_modified=0 THEN excluded.deadline_at ELSE action_items.deadline_at END,
          expiry_at=CASE WHEN action_items.user_modified=0 THEN excluded.expiry_at ELSE action_items.expiry_at END,
          evidence_text=CASE WHEN action_items.user_modified=0 THEN excluded.evidence_text ELSE action_items.evidence_text END,
          updated_at=excluded.updated_at
        """,
        item,
    )
    conn.commit()
    conn.close()


def dismiss_stale_actions(email_id, active_fingerprints):
    conn = _conn()
    if active_fingerprints:
        placeholders = ",".join("?" for _ in active_fingerprints)
        conn.execute(
            f"UPDATE action_items SET status='DISMISSED' WHERE email_id=? AND user_modified=0 "
            f"AND status='OPEN' AND fingerprint NOT IN ({placeholders})",
            [email_id, *active_fingerprints],
        )
    else:
        conn.execute(
            "UPDATE action_items SET status='DISMISSED' WHERE email_id=? AND user_modified=0 AND status='OPEN'",
            (email_id,),
        )
    conn.commit()
    conn.close()


def list_action_items(status="OPEN", limit=200):
    now = datetime.now().astimezone().isoformat()
    conn = _conn()
    conn.execute(
        "UPDATE action_items SET status='EXPIRED', updated_at=? "
        "WHERE status='OPEN' AND expiry_at IS NOT NULL AND expiry_at < ?",
        (now, now),
    )
    sql = """
        SELECT a.*, e.subject, e.sender, e.received_at, e.date, e.provider,
               e.provider_thread_id, e.original_url
        FROM action_items a JOIN emails e ON e.id=a.email_id
    """
    args = []
    if status:
        sql += " WHERE a.status=?"
        args.append(status)
    sql += " ORDER BY CASE a.priority WHEN 'P0_CRITICAL' THEN 0 WHEN 'P1_HIGH' THEN 1 WHEN 'P2_NORMAL' THEN 2 ELSE 3 END, COALESCE(a.deadline_at, '9999'), a.id DESC LIMIT ?"
    args.append(limit)
    rows = conn.execute(sql, args).fetchall()
    conn.commit()
    conn.close()
    return [dict(row) for row in rows]


def set_action_status(action_id, status):
    if status not in {"OPEN", "DONE"}:
        return False
    conn = _conn()
    cur = conn.execute(
        "UPDATE action_items SET status=?, user_modified=1, updated_at=? WHERE id=?",
        (status, datetime.now().astimezone().isoformat(), action_id),
    )
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed


def action_stats():
    conn = _conn()
    counts = {row["status"]: row["c"] for row in conn.execute(
        "SELECT status, COUNT(*) c FROM action_items GROUP BY status"
    )}
    conn.close()
    return counts


def replace_knowledge_document(source_type, source_id, title, source_url, content_hash, chunks):
    """Atomically replace chunks only when canonical document content changes."""
    now = datetime.now().astimezone().isoformat()
    conn = _conn()
    existing = conn.execute(
        "SELECT id, content_hash FROM knowledge_documents WHERE source_type=? AND source_id=?",
        (source_type, source_id),
    ).fetchone()
    if existing and existing["content_hash"] == content_hash:
        conn.close()
        return False
    with conn:
        if existing:
            document_id = existing["id"]
            conn.execute(
                "UPDATE knowledge_documents SET title=?, source_url=?, content_hash=?, indexed_at=? WHERE id=?",
                (title, source_url, content_hash, now, document_id),
            )
            conn.execute("DELETE FROM knowledge_chunks WHERE document_id=?", (document_id,))
        else:
            cur = conn.execute(
                "INSERT INTO knowledge_documents(source_type,source_id,title,source_url,content_hash,indexed_at) VALUES(?,?,?,?,?,?)",
                (source_type, source_id, title, source_url, content_hash, now),
            )
            document_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO knowledge_chunks(document_id,chunk_index,text,embedding,token_count,metadata_json) VALUES(?,?,?,NULL,?,?)",
            [(document_id, index, item["text"], item["token_count"], item["metadata_json"])
             for index, item in enumerate(chunks)],
        )
    conn.close()
    return True


def knowledge_stats():
    conn = _conn()
    documents = conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
    chunks = conn.execute("SELECT COUNT(*) FROM knowledge_chunks").fetchone()[0]
    last_indexed = conn.execute("SELECT MAX(indexed_at) FROM knowledge_documents").fetchone()[0]
    conn.close()
    return {"documents": documents, "chunks": chunks, "last_indexed": last_indexed}


def list_emails_with_analysis():
    conn = _conn()
    rows = conn.execute(
        "SELECT e.*, a.deadline_at, a.deadline_text, a.entities_json, a.labels_json "
        "FROM emails e LEFT JOIN email_analysis a ON a.email_id=e.id ORDER BY e.id"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def replace_topics(items, now):
    """Replace derived topic membership while keeping stable topic ids by key."""
    conn = _conn()
    with conn:
        active_keys = []
        for item in items:
            active_keys.append(item["topic_key"])
            conn.execute(
                """
                INSERT INTO knowledge_topics
                (topic_key,topic_type,title_en,title_zh,summary_en,summary_zh,latest_update_at,deadline_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?)
                ON CONFLICT(topic_key) DO UPDATE SET topic_type=excluded.topic_type,
                  title_en=excluded.title_en,title_zh=excluded.title_zh,summary_en=excluded.summary_en,
                  summary_zh=excluded.summary_zh,latest_update_at=excluded.latest_update_at,
                  deadline_at=excluded.deadline_at,updated_at=excluded.updated_at
                """,
                (item["topic_key"], item["topic_type"], item["title_en"], item["title_zh"],
                 item["summary_en"], item["summary_zh"], item["latest_update_at"], item["deadline_at"], now),
            )
            topic_id = conn.execute(
                "SELECT id FROM knowledge_topics WHERE topic_key=?", (item["topic_key"],)
            ).fetchone()[0]
            conn.execute("DELETE FROM knowledge_topic_emails WHERE topic_id=?", (topic_id,))
            conn.executemany(
                "INSERT INTO knowledge_topic_emails(topic_id,email_id) VALUES(?,?)",
                [(topic_id, email_id) for email_id in item["email_ids"]],
            )
        if active_keys:
            placeholders = ",".join("?" for _ in active_keys)
            conn.execute(f"DELETE FROM knowledge_topics WHERE topic_key NOT IN ({placeholders})", active_keys)
        else:
            conn.execute("DELETE FROM knowledge_topics")
    conn.close()


def list_topics():
    conn = _conn()
    rows = conn.execute(
        """SELECT t.*, COUNT(te.email_id) email_count
           FROM knowledge_topics t LEFT JOIN knowledge_topic_emails te ON te.topic_id=t.id
           GROUP BY t.id ORDER BY CASE t.topic_type WHEN 'PROJECT' THEN 0 WHEN 'COURSE' THEN 1
           WHEN 'SUBSCRIPTION' THEN 2 ELSE 3 END, t.latest_update_at DESC"""
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_topic(topic_id):
    conn = _conn()
    topic = conn.execute("SELECT * FROM knowledge_topics WHERE id=?", (topic_id,)).fetchone()
    emails = conn.execute(
        """SELECT e.* FROM emails e JOIN knowledge_topic_emails te ON te.email_id=e.id
           WHERE te.topic_id=? ORDER BY COALESCE(e.received_at,e.date) DESC, e.id DESC""", (topic_id,)
    ).fetchall()
    conn.close()
    return (dict(topic), [dict(row) for row in emails]) if topic else (None, [])


def list_knowledge_chunks(topic_id=None):
    conn = _conn()
    sql = """SELECT c.id,c.chunk_index,c.text,d.title,d.source_url,CAST(d.source_id AS INTEGER) email_id,e.sender,e.received_at,e.intent,e.priority
             FROM knowledge_chunks c JOIN knowledge_documents d ON d.id=c.document_id
             JOIN emails e ON e.id=CAST(d.source_id AS INTEGER)"""
    args = []
    if topic_id:
        sql += " JOIN knowledge_topic_emails te ON te.email_id=e.id WHERE te.topic_id=?"
        args.append(topic_id)
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_rag_answer(query_id, question, answer, sources, provider):
    now = datetime.now().astimezone().isoformat()
    conn = _conn()
    with conn:
        conn.execute(
            "INSERT INTO rag_queries(id,question,answer,model_provider,model_name,created_at) VALUES(?,?,?,?,?,?)",
            (query_id, question, answer, provider, "", now),
        )
        conn.executemany(
            "INSERT INTO rag_citations(query_id,chunk_id,email_id,rank,score,quoted_text) VALUES(?,?,?,?,?,?)",
            [(query_id, row["id"], row["email_id"], rank, row["score"], row["text"][:500])
             for rank, row in enumerate(sources, 1)],
        )
    conn.close()


def list_analyses_for_action_backfill():
    conn = _conn()
    rows = conn.execute("SELECT * FROM email_analysis ORDER BY email_id").fetchall()
    conn.close()
    results = []
    for row in rows:
        item = dict(row)
        item["intent"] = item.get("category")
        item["action_items"] = json.loads(item.get("action_items_json") or "[]")
        item["requires_action"] = bool(item.get("requires_action"))
        results.append(item)
    return results


def update_sync_state(account_id, folder, uidvalidity, last_uid):
    conn = _conn()
    conn.execute(
        """
        INSERT INTO mail_sync_state(account_id, folder, uidvalidity, last_uid, last_synced_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(account_id, folder) DO UPDATE SET
            uidvalidity=excluded.uidvalidity,
            last_uid=excluded.last_uid,
            last_synced_at=excluded.last_synced_at
        """,
        (account_id, folder, uidvalidity, int(last_uid), datetime.now().astimezone().isoformat()),
    )
    conn.commit()
    conn.close()


def email_exists_by_source(account_id, uidvalidity, source_uid):
    conn = _conn()
    row = conn.execute(
        "SELECT id FROM emails WHERE account_id=? AND uidvalidity=? AND source_uid=?",
        (account_id, uidvalidity, str(source_uid)),
    ).fetchone()
    conn.close()
    return row[0] if row else None


def normalize_existing_forwarded(owner_emails):
    """Repair display sender metadata for already-imported forwarded messages."""
    conn = _conn()
    rows = conn.execute("SELECT id, sender, body_text FROM emails").fetchall()
    updated = 0
    for row in rows:
        message = normalize({"from": row["sender"] or "", "body_text": row["body_text"] or ""}, owner_emails)
        if message.get("forwarded_by"):
            conn.execute(
                "UPDATE emails SET sender=?, forwarded_by=? WHERE id=?",
                (message["from"], message["forwarded_by"], row["id"]),
            )
            updated += 1
    conn.commit()
    conn.close()
    return updated


def list_emails(status=None, intent=None, limit=200):
    conn = _conn()
    sql = "SELECT * FROM emails"
    conds, args = [], []
    if status:
        conds.append("status=?")
        args.append(status)
    if intent:
        conds.append("intent=?")
        args.append(intent)
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY id DESC LIMIT ?"
    args.append(limit)
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_email(email_id):
    conn = _conn()
    row = conn.execute("SELECT * FROM emails WHERE id=?", (email_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_contact(email):
    conn = _conn()
    row = conn.execute("SELECT * FROM contacts WHERE lower(email)=lower(?)", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def stats():
    conn = _conn()
    total = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
    by_status = {r["status"]: r["c"] for r in conn.execute("SELECT status, COUNT(*) c FROM emails GROUP BY status")}
    by_intent = {r["intent"]: r["c"] for r in conn.execute("SELECT intent, COUNT(*) c FROM emails GROUP BY intent")}
    p01 = conn.execute(
        "SELECT COUNT(*) FROM emails WHERE priority IN ('P0_CRITICAL','P1_HIGH')"
    ).fetchone()[0]
    conn.close()
    return {"total": total, "by_status": by_status, "by_intent": by_intent, "p01": p01}


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
