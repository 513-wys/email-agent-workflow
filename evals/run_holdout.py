"""Run the frozen unseen-set audit without changing application rules."""
from __future__ import annotations

import json
from pathlib import Path

from evals.run_baseline import RESULT_DIR, markdown, run


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    result = run(ROOT / "fixtures" / "holdout_email_cases.json", ROOT / "evals" / "holdout_qa_cases.json")
    result["run_type"] = "frozen held-out deterministic evaluation with gold per-message labels"
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "holdout.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (RESULT_DIR / "holdout.md").write_text(markdown(
        result,
        title="Held-out Evaluation Results",
        interpretation=(
            "These cases use unseen course, project, subscription, event, and personal identifiers. "
            "They were evaluated before any rule changes based on their failures. The score is therefore "
            "a more credible estimate of current deterministic generalization than the tuned regression set."
        ),
    ))
    print(json.dumps(result["metrics"], indent=2))
