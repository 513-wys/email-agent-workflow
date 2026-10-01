# Known Holdout After Fix

Dataset: `email-agent-holdout-v1`  
Run type: known-holdout regression after generalization fixes

## Metrics

| Metric | Result |
| --- | ---: |
| Dataset Cases | 10 |
| Topic Assignment Accuracy | 100.0% |
| Action Precision | 100.0% |
| Action Recall | 100.0% |
| Action F1 | 100.0% |
| Rag Micro Source Precision | 100.0% |
| Rag Micro Source Recall | 85.7% |
| Rag Exact Source Set Accuracy | 80.0% |
| Unsupported Question Abstention | 100.0% |

## Material failures

- Topic mismatches: 0 — 
- Action false negatives: none
- Strict RAG source-set failures: 1 — HQA-01

## Interpretation

This run verifies fixes for failures discovered by the first frozen holdout. Because those failures informed the implementation, this is now a regression result, not an unbiased generalization score. A second unseen set is required before claiming improved generalization.

## Limitations

- LLM security, classification, summaries, and answer generation are not scored in this offline run.
- Gold labels are injected so this baseline isolates deterministic downstream behavior.
- Exact source-set accuracy is intentionally strict; extra relevant context still counts as a set mismatch.
