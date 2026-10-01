# Human Evaluation Rubric

This rubric is designed for a reviewer who did not build the system. It complements, rather than replaces, the deterministic regression metrics.

## Scoring protocol

1. Review the 20 synthetic emails in `fixtures/demo_email_cases.json` and the 10 questions in `evals/demo_qa_cases.json`.
2. Inspect the product output and cited source emails without looking at the expected answer first.
3. Score each dimension using the anchors below. Partial credit is allowed.
4. Record concrete evidence and at least one failure or limitation for every dimension below full marks.
5. Do not interpret the tuned-set regression score as a generalization score.

## Rubric (100 points)

| Dimension | Weight | Full-credit anchor |
| --- | ---: | --- |
| Task correctness | 20 | Topics, actions, deadlines, status changes, and superseded facts are consistently correct. |
| Answer completeness and usefulness | 20 | Answers directly address the question, combine all necessary emails, and clearly distinguish completed, pending, optional, and informational items. |
| Retrieval relevance | 15 | Sources are relevant, necessary evidence is not omitted, and unrelated emails are excluded. |
| Citation faithfulness and traceability | 10 | Every material claim is supported by a cited email and the reviewer can open the corresponding source. |
| Safety and privacy | 10 | Suspicious mail is isolated, unsupported questions are refused, public data is synthetic, and secrets/personal data are not committed. |
| Robustness and generalization | 10 | Performance remains credible on unseen phrasings, identifiers, organizations, languages, and larger mailboxes without case-specific tuning. |
| UX and demo readiness | 5 | The English-first demo is understandable, navigable, and tells the user what is simulated versus real. |
| Reproducibility and transparency | 10 | Data, expected labels, eval questions, executable tests, metric definitions, limitations, and run instructions are checked in. |

## Rating anchors

- **90–100 — Excellent:** convincing evidence across both fixed and unseen cases; only minor rough edges.
- **80–89 — Strong:** working and well evidenced, with bounded weaknesses that do not undermine the main claim.
- **70–79 — Credible prototype:** core workflow works, but generalization, answer quality, or deployment evidence is incomplete.
- **60–69 — Partial:** important capabilities work, but major claims lack reliable evidence.
- **Below 60 — Insufficient:** core workflow or supporting evidence is not dependable.

## Bias controls

- The author should not award generalization points merely because all tuned cases pass.
- Retrieval and answer quality must be scored separately: correct sources do not guarantee a good answer.
- A synthetically safe demo cannot by itself prove production security.
- Automated unit-test coverage is evidence of reproducibility, not evidence of real-user usefulness.
