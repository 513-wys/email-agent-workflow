# Live Public Demo Validation

URL: https://email-agent-workflow.onrender.com  
Run at: 2026-10-01T16:20:16.227977+00:00

## Summary

- Surface checks: 5/5
- Exact QA source sets: 10/10
- QA required/forbidden content checks: 10/10

## Surface evidence

- email_count: `20`
- email_count_pass: `True`
- topic_count: `9`
- topic_count_pass: `True`
- open_action_count: `9`
- open_actions_present: `True`
- digest_contains_nova: `True`
- digest_contains_ax4102: `True`
- digest_excludes_quarantined_phishing: `True`

## Question checks

| Case | Sources | Answer content |
| --- | --- | --- |
| QA-01 | PASS | PASS |
| QA-02 | PASS | PASS |
| QA-03 | PASS | PASS |
| QA-04 | PASS | PASS |
| QA-05 | PASS | PASS |
| QA-06 | PASS | PASS |
| QA-07 | PASS | PASS |
| QA-08 | PASS | PASS |
| QA-09 | PASS | PASS |
| QA-10 | PASS | PASS |

This validates the deployed model-free demo, not model-backed answer generation.
