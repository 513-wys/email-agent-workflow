# Offline Final Results

Dataset: `email-agent-public-demo-v2`  
Run type: offline deterministic final evaluation with gold per-message labels

## Metrics

| Metric | Result |
| --- | ---: |
| Dataset Cases | 20 |
| Topic Assignment Accuracy | 100.0% |
| Action Precision | 100.0% |
| Action Recall | 100.0% |
| Action F1 | 100.0% |
| Rag Micro Source Precision | 100.0% |
| Rag Micro Source Recall | 100.0% |
| Rag Exact Source Set Accuracy | 100.0% |
| Unsupported Question Abstention | 100.0% |

## Material failures

- Topic mismatches: 0 — 
- Action false negatives: none
- Strict RAG source-set failures: 0 — 

## Interpretation

This final run uses the exact same 20-message dataset and 10 retrieval questions as the frozen baseline. It measures the effect of the topic, action-policy, and retrieval changes only. Model-backed classification and generated-answer quality remain outside this deterministic run.

## Limitations

- LLM security, classification, summaries, and answer generation are not scored in this offline run.
- Gold labels are injected so this baseline isolates deterministic downstream behavior.
- Exact source-set accuracy is intentionally strict; extra relevant context still counts as a set mismatch.
