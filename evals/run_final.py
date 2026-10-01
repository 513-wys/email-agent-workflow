"""Run the post-tuning evaluation without overwriting the frozen baseline."""
from __future__ import annotations

import json

from evals.run_baseline import RESULT_DIR, markdown, run


if __name__ == "__main__":
    result = run()
    result["run_type"] = "offline deterministic final evaluation with gold per-message labels"
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "final.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    report = markdown(
        result,
        title="Offline Final Results",
        interpretation=(
            "This final run uses the exact same 20-message dataset and 10 retrieval questions as the frozen "
            "baseline. It measures the effect of the topic, action-policy, and retrieval changes only. "
            "Model-backed classification and generated-answer quality remain outside this deterministic run."
        ),
    )
    (RESULT_DIR / "final.md").write_text(report)
    print(json.dumps(result["metrics"], indent=2))
