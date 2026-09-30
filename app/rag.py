"""Local lexical retrieval plus cited cross-email answer generation."""
import re
import uuid

from app import config, db, llm


def _terms(text):
    lowered = (text or "").lower()
    words = set(re.findall(r"[a-z0-9]{2,}", lowered))
    cjk = "".join(re.findall(r"[\u4e00-\u9fff]", lowered))
    words.update(cjk[i:i + 2] for i in range(max(0, len(cjk) - 1)))
    return {word for word in words if word}


def _identifiers(text):
    """Extract explicit identifiers that should behave as hard retrieval filters."""
    value = (text or "").upper()
    pattern = r"(?<![A-Z0-9])(?:PE\d{4}|INC\d{5,}|(?=[A-Z0-9]{6,}(?![A-Z0-9]))(?=[A-Z0-9]*\d)[A-Z0-9]+)(?![A-Z0-9])"
    return set(re.findall(pattern, value))


def retrieve(question, limit=6, topic_id=None):
    query_terms = _terms(question)
    identifiers = _identifiers(question)
    candidates = db.list_knowledge_chunks(topic_id=topic_id)
    scored = []
    for row in candidates:
        searchable = " ".join((row.get("title") or "", row.get("text") or ""))
        if identifiers and not identifiers.issubset(_identifiers(searchable)):
            continue
        text_terms = _terms(searchable)
        score = len(query_terms & text_terms) / max(1, len(query_terms))
        if identifiers:
            score += 1.0
        if score:
            scored.append((score, row))
    scored.sort(key=lambda pair: (pair[0], pair[1]["id"]), reverse=True)
    if not scored:
        return []
    floor = max(0.12, scored[0][0] * 0.45)
    grouped = {}
    for score, row in scored:
        if score < floor:
            continue
        item = grouped.setdefault(row["email_id"], {
            **row, "score": round(score, 4), "text_parts": [], "chunk_ids": [],
        })
        if row["text"] not in [part[1] for part in item["text_parts"]] and len(item["text_parts"]) < 4:
            item["text_parts"].append((row.get("chunk_index", row["id"]), row["text"]))
            item["chunk_ids"].append(row["id"])
    results = []
    for item in grouped.values():
        item["text"] = "\n\n".join(text for _, text in sorted(item.pop("text_parts")))
        results.append(item)
        if len(results) >= limit:
            break
    return results


def answer(question, topic_id=None):
    sources = retrieve(question, topic_id=topic_id)
    if not sources:
        return {"answer": "没有找到足够相关的邮件依据，暂时无法回答。", "sources": []}
    if config.PUBLIC_DEMO:
        chinese = bool(re.search(r"[\u4e00-\u9fff]", question))
        lead = "根据演示邮件，找到以下相关信息：" if chinese else "The demo mailbox contains these relevant updates:"
        bullets = []
        for index, row in enumerate(sources[:4], 1):
            snippet = re.sub(r"\s+", " ", row["text"]).strip()[:320]
            bullets.append(f"- {snippet} [{index}]")
        return {"answer": lead + "\n\n" + "\n".join(bullets), "sources": sources[:4]}
    context = "\n\n".join(f"[{i}] {row['text']}" for i, row in enumerate(sources, 1))
    system = (
        "你是邮件知识库助手。只能使用提供的邮件片段回答，使用与问题相同的语言。"
        "每个事实后标注来源编号，如 [1]。不要编造；依据不足时明确说明。回答简洁、可扫读。"
        "同一来源编号可能包含同一封邮件的多个连续片段，必须综合阅读，不能根据单个片段宣称整封邮件没有相关信息。"
        "主题、摘要和正文的课程编号优先于签名档中的职位或其他课程编号；签名档只用于识别发件人。"
    )
    answer_text = llm.chat_text(system, f"问题：{question}\n\n邮件片段：\n{context}", temperature=0.1, max_tokens=900)
    query_id = str(uuid.uuid4())
    db.save_rag_answer(query_id, question, answer_text, sources, llm.backend_name())
    return {"answer": answer_text, "sources": sources}
