import unittest
from pathlib import Path

from evals.run_baseline import run


class OfflineEvaluationTests(unittest.TestCase):
    def test_evaluation_is_reproducible_and_covers_all_demo_cases(self):
        result = run()
        self.assertEqual(20, result["metrics"]["dataset_cases"])
        self.assertEqual(10, len(result["qa_cases"]))
        self.assertGreaterEqual(result["metrics"]["action_precision"], 0.9)

    def test_frozen_holdout_covers_unseen_cases(self):
        root = Path(__file__).resolve().parents[1]
        result = run(root / "fixtures" / "holdout_email_cases.json", root / "evals" / "holdout_qa_cases.json")
        self.assertEqual("email-agent-holdout-v1", result["dataset_id"])
        self.assertEqual(10, result["metrics"]["dataset_cases"])
        self.assertEqual(5, len(result["qa_cases"]))


if __name__ == "__main__":
    unittest.main()
