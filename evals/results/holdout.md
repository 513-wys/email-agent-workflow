# Held-out Evaluation Results

Dataset: `email-agent-holdout-v1`  
Run type: frozen held-out deterministic evaluation with gold per-message labels

## Metrics

| Metric | Result |
| --- | ---: |
| Dataset Cases | 10 |
| Topic Assignment Accuracy | 10.0% |
| Action Precision | 100.0% |
| Action Recall | 100.0% |
| Action F1 | 100.0% |
| Rag Micro Source Precision | 87.5% |
| Rag Micro Source Recall | 100.0% |
| Rag Exact Source Set Accuracy | 80.0% |
| Unsupported Question Abstention | 0.0% |

## Material failures

- Topic mismatches: 9 — DS5301-H1, DS5301-H2, DS5301-H3, ORION-H1, ORION-H2, TASKFLOW-H1, TASKFLOW-H2, SEMINAR-H1, SEMINAR-H2
- Action false negatives: none
- Strict RAG source-set failures: 1 — HQA-05

## Interpretation

These cases use unseen course, project, subscription, event, and personal identifiers. They were evaluated before any rule changes based on their failures. The score is therefore a more credible estimate of current deterministic generalization than the tuned regression set.

## Limitations

- LLM security, classification, summaries, and answer generation are not scored in this offline run.
- Gold labels are injected so this baseline isolates deterministic downstream behavior.
- Exact source-set accuracy is intentionally strict; extra relevant context still counts as a set mismatch.
