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

## Frozen holdout

`fixtures/holdout_email_cases.json` and `holdout_qa_cases.json` introduce unseen identifiers and wording. Run them with:

```bash
PYTHONPATH=. python evals/run_holdout.py
```

The checked-in `results/holdout.md` and `results/holdout.json` are the first-run results before any holdout-driven rule changes. Keep these files frozen; if the product is tuned against these failures, use a new unseen set to make the next generalization claim.

`results/holdout_after_fix.*` records the regression after the discovered failures were addressed. It must not be presented as a second independent test; its purpose is to show which known failures were fixed and which remain.

The public deployment disables external model calls. Its published evaluation questions use checked-in, model-free synthesis in `app/demo_answers.py`; arbitrary questions fall back to extractive local evidence. This makes the course demo reproducible and auditable, but it is not evidence of model-backed answer quality.
