# Demo Evals

The public demo evals use the same 20 synthetic messages as the visible product demo. This is intentional: the evaluator can inspect every source that produced a score or answer.

`demo_qa_cases.json` tests cross-email synthesis and retrieval precision. A passing answer must:

1. retrieve only relevant topic messages;
2. prefer later updates over superseded facts;
3. distinguish required actions from optional opportunities and informational subscriptions;
4. cite the listed evidence cases;
5. refuse unsupported claims.

Separate programmatic checks will score per-message safety, intent, priority, action extraction, deadlines, topic membership, and idempotency against the `expected` fields in `fixtures/demo_email_cases.json`.

## How to interpret the scores

The deterministic baseline/final runs are regression tests over the same fixed development set. They are not estimates of production accuracy and do not score generated-answer wording or model classification because the runner injects gold per-message labels.

`HUMAN_EVAL_RUBRIC.md` defines a separate 100-point review standard. The current conservative review is recorded in `results/human_evaluation.md` and `results/human_evaluation.json`. It explicitly discounts same-set tuning and identifies the held-out and model-backed evidence still required.
