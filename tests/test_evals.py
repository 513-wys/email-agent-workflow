import unittest

from evals.run_baseline import run


class OfflineBaselineTests(unittest.TestCase):
    def test_baseline_is_reproducible_and_covers_all_demo_cases(self):
        result = run()
        self.assertEqual(20, result["metrics"]["dataset_cases"])
        self.assertEqual(10, len(result["qa_cases"]))
        self.assertEqual(1.0, result["metrics"]["action_precision"])
        self.assertIn("SUB-03", result["action_errors"]["false_negative"])


if __name__ == "__main__":
    unittest.main()
