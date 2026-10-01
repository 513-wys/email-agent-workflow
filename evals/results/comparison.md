# Baseline vs Final Evaluation

Both runs use the same 20 synthetic emails, gold per-message labels, and 10 retrieval questions.

| Metric | Baseline | Final | Change |
| --- | ---: | ---: | ---: |
| Dataset cases | 20 | 20 | — |
| Topic assignment accuracy | 15.0% | 100.0% | +85.0 pp |
| Action precision | 100.0% | 100.0% | +0.0 pp |
| Action recall | 77.8% | 100.0% | +22.2 pp |
| Action F1 | 87.5% | 100.0% | +12.5 pp |
| RAG micro source precision | 26.2% | 100.0% | +73.8 pp |
| RAG micro source recall | 73.3% | 100.0% | +26.7 pp |
| RAG exact source-set accuracy | 10.0% | 100.0% | +90.0 pp |
| Unsupported-question abstention | 0.0% | 100.0% | +100.0 pp |

## Scope

- Topic grouping, action policy, and local lexical retrieval were tuned.
- The frozen baseline files were not overwritten.
- This comparison does not score LLM classification, summary wording, or generated-answer faithfulness.
