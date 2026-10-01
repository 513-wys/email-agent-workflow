# Offline Baseline Results

Dataset: `email-agent-public-demo-v2`  
Run type: offline deterministic baseline with gold per-message labels

## Metrics

| Metric | Result |
| --- | ---: |
| Dataset Cases | 20 |
| Topic Assignment Accuracy | 15.0% |
| Action Precision | 100.0% |
| Action Recall | 77.8% |
| Action F1 | 87.5% |
| Rag Micro Source Precision | 26.2% |
| Rag Micro Source Recall | 73.3% |
| Rag Exact Source Set Accuracy | 10.0% |
| Unsupported Question Abstention | 0.0% |

## Material failures

- Topic mismatches: 17 — AX4102-01, AX4102-02, AX4102-03, AX4102-04, NOVA-01, NOVA-02, NOVA-03, NOVA-04, SEC-02, SUB-01, SUB-02, SUB-03, EVENT-01, EVENT-02, SUPPORT-01, NEWS-01, PERSONAL-01
- Action false negatives: NOVA-03, SUB-03
- Strict RAG source-set failures: 9 — QA-01, QA-02, QA-03, QA-04, QA-05, QA-06, QA-07, QA-08, QA-10

## Interpretation

This is a deliberately honest baseline. It shows how the current deterministic product layer behaves before rules are tuned for the new 20-message dataset. Model-backed classification and answer-quality evaluation remain a separate next step.

## Limitations

- LLM security, classification, summaries, and answer generation are not scored in this offline run.
- Gold labels are injected so this baseline isolates deterministic downstream behavior.
- Exact source-set accuracy is intentionally strict; extra relevant context still counts as a set mismatch.
