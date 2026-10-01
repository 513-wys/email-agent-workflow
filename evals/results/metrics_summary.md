# Evaluation metrics summary

This file separates regression evidence, held-out evidence, live-deployment checks and real-model behaviour. Scores from different rows are not interchangeable.

| Evaluation | Scope | Key results | What it proves |
| --- | --- | --- | --- |
| Fixed deterministic regression | 20 known synthetic emails, 10 known questions; gold per-email analysis | 100% topic/action/retrieval checks | The implemented product logic remains reproducible on the development set; **not** a generalisation estimate. |
| Frozen holdout, first run | 10 unseen emails, 5 unseen questions | Topic key 10%; retrieval precision 87.5%, recall 100%, exact source set 80%; abstention 0% | The original rules overfit identifiers and the refusal threshold was weak. |
| Known holdout after fixes | Same holdout after its failures were inspected | Topic key 100%; retrieval precision 100%, recall 85.7%, exact source set 80%; abstention 100% | The known failures were mostly repaired; **not** a second independent test. |
| Live Render validation | Public deployment with 20 demo emails | 20 emails, 9 topics, 9 actions; 10/10 expected source sets; 10/10 checked-in demo answer checks | The deployed, model-free demonstration is internally consistent and privacy safe. |
| Real DeepSeek triage | 19 safe synthetic emails plus 1 deterministic security-gate case | API success 100%; intent 89.5%; priority 73.7%; action 79.0%; deadline exact 73.7%; median/P95 latency 1.723/2.154 s | Actual configured-model behaviour on the synthetic set. |
| Real DeepSeek RAG answers | 9 generated answers plus 1 deterministic unsupported-question refusal | Exact source sets 100%; strict automated completeness 40%; author semantic review 79%; 6/10 fully acceptable; citations 100%; median/P95 latency 40.894/51.896 s | Retrieval is strong on the known set, but generation can omit facts and made one material security contradiction. |

## Targets and status

| Metric | Target | Reached | Status |
| --- | ---: | ---: | --- |
| Intent classification | ≥85% | 89.5% | Met |
| Priority classification | ≥80% | 73.7% | Not met |
| Action decision | ≥85% | 79.0% | Not met |
| Exact deadline extraction | ≥80% | 73.7% | Not met |
| RAG exact source set | ≥90% | 100% known set / 80% first holdout | Mixed |
| Fully acceptable answers | ≥80% | 60% | Not met |
| Unsupported-question refusal | 100% | 100% current run / 0% first holdout | Mixed |
| Material safety contradictions | 0% | 10% | Not met |
| Median answer latency | ≤15 s | 40.894 s | Not met |

## Main conclusion

The prototype reliably retrieves traceable evidence in the curated demonstration, but it is not a 100%-accurate production assistant. The most important next improvements are an explicit security-alert rule, more complete multi-source answer prompting, calibrated action/priority labels, a second untouched multilingual holdout, and latency/cost telemetry.
