"""Run the reproducible, offline baseline for the synthetic public-demo dataset.

This runner deliberately injects the dataset's gold per-message labels. It therefore
measures the deterministic product layer (topic rules, action policy, indexing and
retrieval), not LLM classification quality. A model-backed eval is reported separately.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from app import actions, config, db, knowledge, rag, topics


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "fixtures" / "demo_email_cases.json"
QA_SET = ROOT / "evals" / "demo_qa_cases.json"
RESULT_DIR = ROOT / "evals" / "results"


def ratio(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else 1.0


def category_code(value):
    aliases = {
        "Education notice": "EDUCATION_NOTICE", "Project update": "PROJECT_UPDATE",
        "Action required": "ACTION_REQUIRED", "Security alert": "SECURITY_ALERT",
        "Security interception": "SECURITY_ALERT", "Payment and billing": "PAYMENT_BILLING",
        "Newsletter": "NEWSLETTER", "Meeting and calendar": "MEETING_CALENDAR",
        "Customer support": "CUSTOMER_SUPPORT", "Personal": "PERSONAL",
    }
    return aliases[value]


def analysis_for(case):
    expected = case["expected"]
    action_title = expected.get("action") or expected.get("conditional_action")
    action_items = []
    if action_title:
        action_items.append({
            "title": action_title,
            "evidence": case["body"],
            "deadline_at": expected.get("deadline"),
        })
    entities = []
    if case["id"].startswith("AX4102"):
        entities.append({"type": "COURSE", "value": "AX4102"})
    if case["id"].startswith("NOVA"):
        entities.append({"type": "PROJECT", "value": "Project NOVA"})
    if case["id"].startswith("SUB"):
        entities.append({"type": "ORGANIZATION", "value": "CloudNotes"})
    if case["id"] == "NEWS-01":
        entities.append({"type": "ORGANIZATION", "value": "Agent Systems Weekly"})
    return {
        "intent": expected["intent"], "priority": expected["priority"], "confidence": 1.0,
        "requires_action": expected.get("requires_action", False), "requires_reply": False,
        "deadline_at": expected.get("deadline"), "deadline_text": None,
        "labels": [expected["topic"]] if expected.get("topic") else [],
        "entities": entities, "reason_codes": ["GOLD_FIXTURE"],
        "model_provider": "gold", "model_name": "", "prompt_version": "eval-v1",
        "action_items": action_items,
    }


def record_for(case, index):
    expected = case["expected"]
    safe = expected.get("safe", True)
    provider = {"gmail": "GMAIL", "outlook": "OUTLOOK", "university_forwarded": "DEMO"}[case["source"]]
    return {
        "trace_id": case["id"], "message_id": f"<{case['id']}@example.invalid>",
        "sender": case["sender"], "subject": case["subject"], "body_text": case["body"],
        "date": case["received_at"], "gmail_link": "", "threat_score": 95 if not safe else 0,
        "risk_level": "CRITICAL" if not safe else "LOW", "is_safe": int(safe),
        "intent": expected["intent"], "category": category_code(expected["category"]),
        "priority": expected["priority"], "sentiment": "NEUTRAL", "language": "en-US",
        "summary": case["body"], "summary_zh": "", "context_json": "{}",
        "status": "已隔离" if not safe else "已分类", "created_at": case["received_at"],
        "account_id": case["account"], "provider": provider, "source_uid": str(index),
        "internet_message_id": "", "provider_message_id": case["id"],
        "received_at": case["received_at"], "original_url": "", "content_hash": case["id"],
        "uidvalidity": "eval-v1", "provider_thread_id": case["id"],
        "forwarded_by": "demo.student@example.com" if case["source"] == "university_forwarded" else "",
    }


def run(dataset_path=DATASET, qa_path=QA_SET):
    dataset_document = json.loads(Path(dataset_path).read_text())
    dataset = dataset_document["cases"]
    qa_cases = json.loads(Path(qa_path).read_text())["evals"]
    with tempfile.TemporaryDirectory() as temp_dir, patch.object(config, "DB_PATH", Path(temp_dir) / "baseline.db"):
        db.init_db()
        email_ids = {}
        topic_rows = []
        expected_action_ids = set()
        for index, case in enumerate(dataset, 1):
            analysis = analysis_for(case)
            record = record_for(case, index)
            email_id = db.insert_email(record)
            email_ids[email_id] = case["id"]
            db.upsert_email_analysis(email_id, analysis)
            if record["is_safe"]:
                knowledge.index_email(db.get_email(email_id))
                actions.sync(email_id, analysis)
            if analysis["action_items"] and case["expected"].get("requires_action"):
                expected_action_ids.add(case["id"])
            predicted_topic = None if not record["is_safe"] else topics.classify(record, {
                "labels_json": json.dumps(analysis["labels"]),
                "entities_json": json.dumps(analysis["entities"]),
            })[0]
            topic_rows.append({
                "id": case["id"], "expected": case["expected"].get("topic"),
                "predicted": predicted_topic,
                "correct": predicted_topic == case["expected"].get("topic"),
            })

        open_actions = db.list_action_items("OPEN", limit=100)
        predicted_action_ids = {email_ids[row["email_id"]] for row in open_actions}
        action_tp = len(predicted_action_ids & expected_action_ids)
        action_precision = ratio(action_tp, len(predicted_action_ids))
        action_recall = ratio(action_tp, len(expected_action_ids))
        action_f1 = ratio(2 * action_precision * action_recall, action_precision + action_recall)

        qa_rows = []
        total_expected, total_returned, total_relevant = 0, 0, 0
        abstain_correct = 0
        for item in qa_cases:
            retrieved = rag.retrieve(item["question"], limit=6)
            returned = [email_ids[row["email_id"]] for row in retrieved]
            expected = item["expected_source_ids"]
            relevant = len(set(returned) & set(expected))
            total_expected += len(expected)
            total_returned += len(returned)
            total_relevant += relevant
            if item.get("behavior") == "abstain" and not returned:
                abstain_correct += 1
            qa_rows.append({
                "id": item["id"], "expected_sources": expected, "returned_sources": returned,
                "source_precision": ratio(relevant, len(returned)),
                "source_recall": ratio(relevant, len(expected)),
                "pass": set(returned) == set(expected),
            })

        topic_correct = sum(row["correct"] for row in topic_rows)
        metrics = {
            "dataset_cases": len(dataset),
            "topic_assignment_accuracy": ratio(topic_correct, len(topic_rows)),
            "action_precision": action_precision,
            "action_recall": action_recall,
            "action_f1": action_f1,
            "rag_micro_source_precision": ratio(total_relevant, total_returned),
            "rag_micro_source_recall": ratio(total_relevant, total_expected),
            "rag_exact_source_set_accuracy": ratio(sum(row["pass"] for row in qa_rows), len(qa_rows)),
            "unsupported_question_abstention": ratio(abstain_correct, 1),
        }
        return {
            "run_type": "offline deterministic baseline with gold per-message labels",
            "dataset_id": dataset_document["dataset_id"], "metrics": metrics,
            "topic_cases": topic_rows,
            "action_errors": {
                "false_positive": sorted(predicted_action_ids - expected_action_ids),
                "false_negative": sorted(expected_action_ids - predicted_action_ids),
            },
            "qa_cases": qa_rows,
            "limitations": [
                "LLM security, classification, summaries, and answer generation are not scored in this offline run.",
                "Gold labels are injected so this baseline isolates deterministic downstream behavior.",
                "Exact source-set accuracy is intentionally strict; extra relevant context still counts as a set mismatch."
            ],
        }


def markdown(result, title="Offline Baseline Results", interpretation=None):
    m = result["metrics"]
    misses = [row for row in result["topic_cases"] if not row["correct"]]
    qa_misses = [row for row in result["qa_cases"] if not row["pass"]]
    lines = [
        f"# {title}", "",
        f"Dataset: `{result['dataset_id']}`  ",
        f"Run type: {result['run_type']}", "",
        "## Metrics", "",
        "| Metric | Result |", "| --- | ---: |",
    ]
    for key, value in m.items():
        shown = str(value) if key == "dataset_cases" else f"{value * 100:.1f}%"
        lines.append(f"| {key.replace('_', ' ').title()} | {shown} |")
    lines.extend(["", "## Material failures", ""])
    lines.append(f"- Topic mismatches: {len(misses)} — " + ", ".join(row["id"] for row in misses))
    lines.append(f"- Action false negatives: {', '.join(result['action_errors']['false_negative']) or 'none'}")
    lines.append(f"- Strict RAG source-set failures: {len(qa_misses)} — " + ", ".join(row["id"] for row in qa_misses))
    lines.extend(["", "## Interpretation", "",
        interpretation or "This is a deliberately honest baseline. It shows how the current deterministic product layer behaves before rules are tuned for the new 20-message dataset. Model-backed classification and answer-quality evaluation remain a separate next step.",
        "", "## Limitations", ""])
    lines.extend(f"- {item}" for item in result["limitations"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    result = run()
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "baseline.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (RESULT_DIR / "baseline.md").write_text(markdown(result))
    print(json.dumps(result["metrics"], indent=2))
