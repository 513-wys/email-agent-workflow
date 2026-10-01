"""Evaluate real model classification and cited answers on synthetic data only."""
from __future__ import annotations

import json
import re
import statistics
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from app import config, db, knowledge, rag, security, settings_store, triage
from evals.run_baseline import analysis_for, record_for


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "evals" / "results"


def ratio(a, b):
    return round(a / b, 4) if b else 0.0


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, int((len(ordered) - 1) * fraction))], 3)


def claim_covered(claim, answer):
    ignored = {"a", "an", "the", "is", "are", "was", "were", "has", "have", "been", "it", "its", "for", "to"}
    required = set(re.findall(r"[a-z0-9]+", claim.lower())) - ignored
    present = set(re.findall(r"[a-z0-9]+", answer.lower()))
    return required.issubset(present)


def run():
    dataset = json.loads((ROOT / "fixtures" / "demo_email_cases.json").read_text())
    qa_set = json.loads((ROOT / "evals" / "demo_qa_cases.json").read_text())
    classification_rows, classification_latencies = [], []

    for case in dataset["cases"]:
        expected = case["expected"]
        email = {
            "from": case["sender"], "subject": case["subject"], "body_text": case["body"],
            "received_at": case["received_at"],
        }
        safety_result = security.evaluate(email)
        if not expected.get("safe", True):
            classification_rows.append({
                "id": case["id"], "stage": "security_gate",
                "expected_safe": False, "predicted_safe": safety_result["is_safe"],
                "pass": not safety_result["is_safe"],
            })
            continue
        started = time.perf_counter()
        try:
            prediction = triage.classify(email)
            latency = time.perf_counter() - started
            classification_latencies.append(latency)
            row = {
                "id": case["id"], "stage": "model_triage", "success": True,
                "latency_seconds": round(latency, 3),
                "expected_intent": expected["intent"], "predicted_intent": prediction["intent"],
                "intent_correct": prediction["intent"] == expected["intent"],
                "expected_priority": expected["priority"], "predicted_priority": prediction["priority"],
                "priority_correct": prediction["priority"] == expected["priority"],
                "expected_requires_action": expected.get("requires_action", False),
                "predicted_requires_action": prediction["requires_action"],
                "requires_action_correct": prediction["requires_action"] == expected.get("requires_action", False),
                "expected_deadline": expected.get("deadline"), "predicted_deadline": prediction["deadline_at"],
                "deadline_correct": prediction["deadline_at"] == expected.get("deadline"),
                "summary_present": bool(prediction["summary"].strip()),
                "chinese_summary_present": bool(prediction["summary_zh"].strip()),
            }
        except Exception as exc:
            latency = time.perf_counter() - started
            classification_latencies.append(latency)
            row = {"id": case["id"], "stage": "model_triage", "success": False,
                   "latency_seconds": round(latency, 3), "error_type": type(exc).__name__}
        classification_rows.append(row)
        print(f"classified {case['id']}: {row.get('success', row.get('pass'))}", flush=True)

    safe_model_rows = [row for row in classification_rows if row["stage"] == "model_triage"]
    successful_model_rows = [row for row in safe_model_rows if row.get("success")]
    security_rows = [row for row in classification_rows if row["stage"] == "security_gate"]

    qa_rows, qa_latencies = [], []
    with tempfile.TemporaryDirectory() as temp_dir, patch.object(config, "DB_PATH", Path(temp_dir) / "model-eval.db"), patch.object(config, "PUBLIC_DEMO", False):
        db.init_db()
        settings_store.init_table()
        email_ids = {}
        for index, case in enumerate(dataset["cases"], 1):
            record = record_for(case, index)
            email_id = db.insert_email(record)
            email_ids[email_id] = case["id"]
            db.upsert_email_analysis(email_id, analysis_for(case))
            if record["is_safe"]:
                knowledge.index_email(db.get_email(email_id))
        for item in qa_set["evals"]:
            started = time.perf_counter()
            try:
                response = rag.answer(item["question"])
                latency = time.perf_counter() - started
                qa_latencies.append(latency)
                returned = [email_ids[source["email_id"]] for source in response["sources"]]
                required_ok = all(claim_covered(claim, response["answer"]) for claim in item.get("must_include", []))
                forbidden_ok = all(claim.lower() not in response["answer"].lower() for claim in item.get("must_not_include", []))
                citations_ok = not returned or bool(re.search(r"\[\d+\]", response["answer"]))
                row = {
                    "id": item["id"], "success": True, "latency_seconds": round(latency, 3),
                    "expected_sources": item["expected_source_ids"], "returned_sources": returned,
                    "source_set_correct": set(returned) == set(item["expected_source_ids"]),
                    "required_content_correct": required_ok, "forbidden_content_correct": forbidden_ok,
                    "citations_present": citations_ok, "answer": response["answer"],
                }
            except Exception as exc:
                latency = time.perf_counter() - started
                qa_latencies.append(latency)
                row = {"id": item["id"], "success": False, "latency_seconds": round(latency, 3),
                       "error_type": type(exc).__name__}
            qa_rows.append(row)
            print(f"answered {item['id']}: {row.get('success')}", flush=True)

    successful_qa = [row for row in qa_rows if row.get("success")]
    metrics = {
        "synthetic_email_cases": len(dataset["cases"]),
        "security_gate_accuracy": ratio(sum(row.get("pass", False) for row in security_rows), len(security_rows)),
        "model_triage_success_rate": ratio(len(successful_model_rows), len(safe_model_rows)),
        "intent_accuracy": ratio(sum(row["intent_correct"] for row in successful_model_rows), len(successful_model_rows)),
        "priority_accuracy": ratio(sum(row["priority_correct"] for row in successful_model_rows), len(successful_model_rows)),
        "requires_action_accuracy": ratio(sum(row["requires_action_correct"] for row in successful_model_rows), len(successful_model_rows)),
        "deadline_exact_accuracy": ratio(sum(row["deadline_correct"] for row in successful_model_rows), len(successful_model_rows)),
        "summary_presence_rate": ratio(sum(row["summary_present"] and row["chinese_summary_present"] for row in successful_model_rows), len(successful_model_rows)),
        "triage_latency_median_seconds": round(statistics.median(classification_latencies), 3) if classification_latencies else None,
        "triage_latency_p95_seconds": percentile(classification_latencies, 0.95),
        "model_answer_success_rate": ratio(len(successful_qa), len(qa_rows)),
        "generated_answer_cases": sum(bool(row.get("returned_sources")) for row in successful_qa),
        "deterministic_abstention_cases": sum(not row.get("returned_sources") for row in successful_qa),
        "answer_exact_source_set_accuracy": ratio(sum(row["source_set_correct"] for row in successful_qa), len(successful_qa)),
        "answer_required_content_accuracy": ratio(sum(row["required_content_correct"] for row in successful_qa), len(successful_qa)),
        "answer_forbidden_content_accuracy": ratio(sum(row["forbidden_content_correct"] for row in successful_qa), len(successful_qa)),
        "answer_citation_presence_rate": ratio(sum(row["citations_present"] for row in successful_qa), len(successful_qa)),
        "answer_latency_median_seconds": round(statistics.median(qa_latencies), 3) if qa_latencies else None,
        "answer_latency_p95_seconds": percentile(qa_latencies, 0.95),
    }
    return {
        "evaluation_type": "model-backed synthetic evaluation", "backend": "deepseek",
        "run_at": datetime.now(timezone.utc).isoformat(), "metrics": metrics,
        "classification_cases": classification_rows, "qa_cases": qa_rows,
        "limitations": [
            "All content is synthetic and English; this does not measure real-mail distribution shift.",
            "Gold analysis is used only to construct the RAG index; generated answers use the real configured model.",
            "API token usage and monetary cost are unavailable because the current client does not persist usage metadata.",
            "Content checks are automated claim-token coverage and should be supplemented by independent human review."
        ],
    }


if __name__ == "__main__":
    result = run()
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "model_evaluation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    m = result["metrics"]
    lines = ["# Model-backed Evaluation", "", f"Backend: `{result['backend']}`  ", f"Run at: {result['run_at']}", "", "## Metrics", "", "| Metric | Result |", "| --- | ---: |"]
    for key, value in m.items():
        if key.endswith("seconds"):
            shown = "unavailable" if value is None else f"{value:.3f} s"
        elif key.endswith("cases"):
            shown = str(value)
        else:
            shown = f"{value * 100:.1f}%"
        lines.append(f"| {key.replace('_', ' ').title()} | {shown} |")
    lines.extend(["", "## Failures", ""])
    triage_failures = [row["id"] for row in result["classification_cases"] if row.get("success") is False]
    qa_failures = [row["id"] for row in result["qa_cases"] if not row.get("success") or not (row.get("source_set_correct") and row.get("required_content_correct") and row.get("forbidden_content_correct") and row.get("citations_present"))]
    lines.append(f"- Triage call failures: {', '.join(triage_failures) or 'none'}")
    lines.append(f"- QA cases with any failed criterion: {', '.join(qa_failures) or 'none'}")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in result["limitations"])
    (RESULT_DIR / "model_evaluation.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(result["metrics"], indent=2))
