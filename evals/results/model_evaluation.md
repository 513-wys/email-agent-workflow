# Model-backed Evaluation

Backend: `deepseek`  
Run at: 2026-10-01T16:31:20.116654+00:00

## Metrics

| Metric | Result |
| --- | ---: |
| Synthetic Email Cases | 20 |
| Security Gate Accuracy | 100.0% |
| Model Triage Success Rate | 100.0% |
| Intent Accuracy | 89.5% |
| Priority Accuracy | 73.7% |
| Requires Action Accuracy | 79.0% |
| Deadline Exact Accuracy | 73.7% |
| Summary Presence Rate | 100.0% |
| Triage Latency Median Seconds | 1.723 s |
| Triage Latency P95 Seconds | 2.154 s |
| Model Answer Success Rate | 100.0% |
| Generated Answer Cases | 9 |
| Deterministic Abstention Cases | 1 |
| Answer Exact Source Set Accuracy | 100.0% |
| Answer Required Content Accuracy | 40.0% |
| Answer Forbidden Content Accuracy | 100.0% |
| Answer Citation Presence Rate | 100.0% |
| Answer Latency Median Seconds | 40.894 s |
| Answer Latency P95 Seconds | 51.896 s |

## Failures

- Triage call failures: none
- QA cases with any failed criterion: QA-01, QA-03, QA-06, QA-07, QA-08, QA-09

## Limitations

- All content is synthetic and English; this does not measure real-mail distribution shift.
- Gold analysis is used only to construct the RAG index; generated answers use the real configured model.
- API token usage and monetary cost are unavailable because the current client does not persist usage metadata.
- Content checks are automated claim-token coverage and should be supplemented by independent human review.
