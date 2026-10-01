import unittest

from evals.run_baseline import run


class OfflineEvaluationTests(unittest.TestCase):
    def test_evaluation_is_reproducible_and_covers_all_demo_cases(self):
        result = run()
        self.assertEqual(20, result["metrics"]["dataset_cases"])
        self.assertEqual(10, len(result["qa_cases"]))
        self.assertGreaterEqual(result["metrics"]["action_precision"], 0.9)


if __name__ == "__main__":
    unittest.main()
