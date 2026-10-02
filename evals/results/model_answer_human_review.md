# Model-answer semantic review

Review date: 2026-10-02  
Reviewer: project author acting under the checked-in rubric (not an independent blind reviewer)  
Evidence: the saved DeepSeek answers in `model_evaluation.json`

Each answer receives up to 5 points: 2 for correctness, 2 for completeness, and 1 for citation/refusal behaviour. This review exists because the strict automated phrase checker penalises harmless word-order changes, while also making it possible to identify genuine omissions and contradictions.

| Case | Score | Review |
| --- | ---: | --- |
| QA-01 | 3.5/5 | Correctly says no further action remains, but omits the useful context that the proposal was submitted under the extended deadline. |
| QA-02 | 5/5 | Correct deadline, format and rubric weights with a source citation. |
| QA-03 | 5/5 | Complete release-package contents and dates; the automated failure is only a word-order mismatch. |
| QA-04 | 5/5 | All three regression gaps are present and supported. |
| QA-05 | 5/5 | Correctly reconciles the old and new venue and preserves the unchanged time. |
| QA-06 | 3/5 | Correctly explains CloudNotes billing, but incorrectly says there is only one subscription and omits the informational newsletter/update items. |
| QA-07 | 0/5 | Material safety failure: it calls a legitimate account alert phishing even though the source labels it legitimate. |
| QA-08 | 5/5 | Correct status, restored access and conditional reopen instruction; automated wording check was too strict. |
| QA-09 | 3/5 | Gives the Helio Robotics deadline but omits the career-talk registration deadline. |
| QA-10 | 5/5 | Correctly refuses an unsupported flight-booking question without inventing sources. |
| **Total** | **39.5/50 (79%)** | Six answers are fully acceptable; three are incomplete and one is materially wrong. |

## Defensible interpretation

- Exact retrieval source sets: **10/10** on this known synthetic set.
- Fully acceptable generated answers: **6/10**.
- Partial-credit semantic score: **79%**.
- Unsupported-question refusal: **1/1**.
- Materially unsafe or contradictory answer: **1/10** (QA-07).

This is an author-scored semantic review, not an independent human study. The saved answers allow a teacher or TA to reproduce or replace the judgements.
