"""Validate the deployed public demo as a user sees it."""
from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://email-agent-workflow.onrender.com"
RESULT_DIR = ROOT / "evals" / "results"


def fetch(path, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    request = urllib.request.Request(BASE_URL + path, data=body)
    return urllib.request.urlopen(request, timeout=60).read().decode()


def visible_text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def run():
    dataset = json.loads((ROOT / "fixtures" / "demo_email_cases.json").read_text())
    qa_set = json.loads((ROOT / "evals" / "demo_qa_cases.json").read_text())
    subjects = {case["id"]: case["subject"] for case in dataset["cases"]}

    emails_page = fetch("/emails")
    knowledge_page = fetch("/knowledge")
    actions_page = fetch("/actions")
    digest_page = fetch("/digest", {"generate": "1"})

    qa_rows = []
    for item in qa_set["evals"]:
        page = fetch("/knowledge/ask", {"question": item["question"]})
        source_block = re.search(r'<ol class="citation-list">(.*?)</ol>', page, re.S)
        returned = [] if not source_block else [
            visible_text(value) for value in re.findall(r"<a[^>]*>(.*?)</a>", source_block.group(1), re.S)
        ]
        answer_match = re.search(r'<div class="answer-text">(.*?)</div>', page, re.S)
        answer = visible_text(answer_match.group(1)) if answer_match else ""
        expected = [subjects[source_id] for source_id in item["expected_source_ids"]]
        required = item.get("must_include", [])
        forbidden = item.get("must_not_include", [])
        content_pass = all(value.lower() in answer.lower() for value in required)
        forbidden_pass = all(value.lower() not in answer.lower() for value in forbidden)
        qa_rows.append({
            "id": item["id"], "expected_source_titles": expected, "returned_source_titles": returned,
            "source_set_pass": set(returned) == set(expected),
            "required_answer_content_pass": content_pass,
            "forbidden_answer_content_pass": forbidden_pass,
            "answer": answer,
        })

    email_links = set(re.findall(r'href="/emails/(\d+)"', emails_page))
    topic_links = set(re.findall(r'href="/knowledge/topics/(\d+)"', knowledge_page))
    action_count = len(re.findall(r'<article class="action-item', actions_page))
    digest_text = visible_text(digest_page)
    surfaces = {
        "email_count": len(email_links), "email_count_pass": len(email_links) == 20,
        "topic_count": len(topic_links), "topic_count_pass": len(topic_links) >= 8,
        "open_action_count": action_count, "open_actions_present": action_count >= 8,
        "digest_contains_nova": "Project NOVA" in digest_text,
        "digest_contains_ax4102": "AX4102" in digest_text,
        "digest_excludes_quarantined_phishing": "mailbox suspension" not in digest_text,
    }
    return {
        "validation_type": "live deployed public-demo validation",
        "base_url": BASE_URL,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "surfaces": surfaces,
        "qa_cases": qa_rows,
        "summary": {
            "surface_checks_passed": sum(bool(value) for key, value in surfaces.items() if key.endswith("pass") or key.startswith("digest_")),
            "surface_checks_total": sum(1 for key in surfaces if key.endswith("pass") or key.startswith("digest_")),
            "qa_source_sets_passed": sum(row["source_set_pass"] for row in qa_rows),
            "qa_source_sets_total": len(qa_rows),
            "qa_content_checks_passed": sum(row["required_answer_content_pass"] and row["forbidden_answer_content_pass"] for row in qa_rows),
            "qa_content_checks_total": len(qa_rows),
        },
    }


if __name__ == "__main__":
    result = run()
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "live_demo_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    summary = result["summary"]
    lines = [
        "# Live Public Demo Validation", "", f"URL: {result['base_url']}  ", f"Run at: {result['run_at']}", "",
        "## Summary", "",
        f"- Surface checks: {summary['surface_checks_passed']}/{summary['surface_checks_total']}",
        f"- Exact QA source sets: {summary['qa_source_sets_passed']}/{summary['qa_source_sets_total']}",
        f"- QA required/forbidden content checks: {summary['qa_content_checks_passed']}/{summary['qa_content_checks_total']}",
        "", "## Surface evidence", "",
    ]
    lines.extend(f"- {key}: `{value}`" for key, value in result["surfaces"].items())
    lines.extend(["", "## Question checks", "", "| Case | Sources | Answer content |", "| --- | --- | --- |"])
    for row in result["qa_cases"]:
        content_ok = row["required_answer_content_pass"] and row["forbidden_answer_content_pass"]
        lines.append(f"| {row['id']} | {'PASS' if row['source_set_pass'] else 'FAIL'} | {'PASS' if content_ok else 'FAIL'} |")
    lines.extend(["", "This validates the deployed extractive demo, not model-backed answer generation.", ""])
    (RESULT_DIR / "live_demo_validation.md").write_text("\n".join(lines))
    print(json.dumps(result["summary"], indent=2))
