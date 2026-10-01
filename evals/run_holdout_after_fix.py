"""Record known-holdout regression after fixes; not a new generalization estimate."""
from __future__ import annotations

import json
from pathlib import Path

from evals.run_baseline import RESULT_DIR, markdown, run


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    result = run(ROOT / "fixtures" / "holdout_email_cases.json", ROOT / "evals" / "holdout_qa_cases.json")
    result["run_type"] = "known-holdout regression after generalization fixes"
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "holdout_after_fix.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (RESULT_DIR / "holdout_after_fix.md").write_text(markdown(
        result,
        title="Known Holdout After Fix",
        interpretation=(
            "This run verifies fixes for failures discovered by the first frozen holdout. Because those failures "
            "informed the implementation, this is now a regression result, not an unbiased generalization score. "
            "A second unseen set is required before claiming improved generalization."
        ),
    ))
    print(json.dumps(result["metrics"], indent=2))
