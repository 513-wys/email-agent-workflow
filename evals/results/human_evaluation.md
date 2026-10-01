# Simulated Independent Human Evaluation

Evaluation date: 1 October 2026  
Evaluated artifact: `email-agent-public-demo-v2`  
Rubric: `evals/HUMAN_EVAL_RUBRIC.md`

## Executive result

**Overall score: 71/100 — Credible prototype**

The system demonstrates a coherent, privacy-safe email workflow and a reproducible evaluation harness. Its strongest evidence is action handling, source traceability, and public-demo isolation. A newly frozen 10-email/5-question holdout achieved 87.5% retrieval precision, 100% retrieval recall, and 80% exact source sets, but only 10% strict topic-key accuracy and failed its unsupported-question abstention case. This confirms that the tuned 100% regression result does not generalize uniformly. The public demo's answer path is also extractive rather than a separately evaluated synthesis model.

## Scorecard

| Dimension | Score | Weight | Reviewer evidence and deductions |
| --- | ---: | ---: | --- |
| Task correctness | 14 | 20 | The fixed set passes, but strict topic-key accuracy falls to 10% on unseen course, project, subscription, and event names. The run also injects gold per-message labels and does not measure model classification quality. |
| Answer completeness and usefulness | 13 | 20 | The 10 questions specify strong content expectations, including superseded facts and multi-email synthesis. However, the offline runner scores source sets rather than the wording, completeness, or readability of generated answers; public-demo answers are extractive snippets. |
| Retrieval relevance | 13 | 15 | The held-out set reaches 87.5% micro precision, 100% recall, and 80% exact source sets. This is useful but not yet broad enough for a high-confidence generalization claim. |
| Citation faithfulness and traceability | 8 | 10 | Retrieved emails are exposed as sources and answers use numbered citations. Deducted because claim-level citation correctness has not been independently annotated or scored. |
| Safety and privacy | 8 | 10 | Public data uses reserved fictional domains; the phishing case is quarantined; demo mode disables mailbox/API access. The held-out unsupported hotel question was not rejected, and this is not a production security audit. |
| Robustness and generalization | 2 | 10 | The frozen holdout exposes substantial dependence on known identifiers and lexical patterns. There is still no bilingual RAG suite, large-mailbox/load test, or adversarial model evaluation. |
| UX and demo readiness | 4 | 5 | The application has an English-first demo, Chinese switch, onboarding, dashboard, knowledge, actions, digest, and simulated original-email view. Deducted because a complete moderated user test and final 20-message deployed walkthrough have not yet been documented. |
| Reproducibility and transparency | 9 | 10 | Development data, a separately frozen holdout, expected labels, QA sets, executable runners, results, README, product documentation, and architecture are checked in. A model-backed result and independent reviewer annotation are still missing. |
| **Total** | **71** | **100** | **Credible prototype; not a production-quality or generalized 100% system.** |

## Manual question-level assessment

| Case | Retrieval | Expected answer difficulty | Human assessment |
| --- | --- | --- | --- |
| QA-01 AX4102 remaining work | Correct fixed-set sources | Must reconcile submission confirmation with deadline update | Good evidence selection; generated synthesis still needs manual wording review. |
| QA-02 AX4102 deadline/rubric | Correct fixed-set source | Must reject superseded 4 October deadline | Strong deterministic retrieval. |
| QA-03 NOVA deliverables | Correct fixed-set source | Multiple deliverables and one deadline | Strong evidence selection. |
| QA-04 NOVA eval gaps | Correct fixed-set source | Enumerated regression gaps | Strong evidence selection. |
| QA-05 roundtable change | Correct fixed-set sources | Must combine old and new venue facts | Good temporal case, but rule is lexically narrow. |
| QA-06 subscriptions | Correct fixed-set sources | Must separate informational updates from failed payment | Useful representative case; current retrieval filtering is category-dependent. |
| QA-07 phishing judgment | Correct fixed-set source | Must avoid citing quarantined phishing content as truth | Good safety behavior in this fixture. |
| QA-08 support status | Correct fixed-set source | Status plus conditional reopening instruction | Strong single-source case. |
| QA-09 career deadlines | Correct fixed-set sources | Optional registration versus application deadline | Good distinction in fixture; unseen phrasing remains untested. |
| QA-10 unsupported travel question | Correct abstention | Must not fabricate | Strong fixed-set refusal case. |

## Interpretation of the 100% regression result

The final deterministic run is valuable as a **regression gate**: future code changes should not break these 20 messages and 10 questions. It is not an unbiased estimate of real-world accuracy because:

1. the same examples informed the rule changes;
2. gold intent, priority, and action labels are injected;
3. generated answer text is not scored;
4. no held-out distribution or blind reviewer was used;
5. the dataset is small and intentionally structured.

For the report, the defensible claim is: **“The tuned deterministic layer achieved 100% on its fixed regression set. On a separately frozen holdout, retrieval reached 87.5% precision, 100% recall, and 80% exact source sets, while strict topic-key accuracy was 10% and unsupported-question abstention failed. A rubric-based simulated human audit therefore scored the overall prototype 71/100.”**

## Required next evidence

1. Keep the current 20 cases as the development/regression set and the 10-email holdout frozen.
2. Diagnose holdout failures, then validate any improvements on a second unseen set rather than reusing this holdout as proof.
3. Save actual model answers and have a reviewer score completeness, faithfulness, and citation support using this rubric.
4. Add Chinese questions and ambiguous/hostile inputs.
5. Record latency, failure rate, and approximate model cost for a complete import and QA run.
6. Document a short usability walkthrough of the deployed 20-message demo.

## Submission-artifact check

| Teacher requirement | Current evidence | Status |
| --- | --- | --- |
| Problem statement | `README.md`, `PRODUCT.md` | Present |
| Business and technical trade-off analysis within report limit | Not yet assembled as the final ≤1,200-word report | **Missing final deliverable** |
| Working GitHub code | Repository plus run/deploy instructions | Present |
| Recorded 5 ± 3 minute demo with presenter and screen | No checked-in video evidence | **Missing final deliverable** |
| Transparent data and explainer | `fixtures/demo_email_cases.json`, `fixtures/README.md` | Present |
| Transparent evals and explainer | `evals/demo_qa_cases.json`, `evals/README.md`, this rubric and result | Present |
| Legible module-level code documentation | Module docstrings, README module map, architecture documentation | Mostly present |
| Persona, input, output, architecture | `PRODUCT.md`, `README.md`, `ARCHITECTURE.md` | Present |
| Targeted metrics and reached metrics | Baseline/final comparison, frozen holdout, and human score | Present, but model-backed metrics remain missing |

This checklist should be updated again immediately before submission.

## Post-review engineering note

The first holdout was kept unchanged. General topic extraction and unsupported-query filtering were subsequently improved and recorded separately in `holdout_after_fix.*`. That rerun reaches 100% topic-key accuracy and unsupported-question abstention, while strict RAG source-set accuracy remains 80% because one multi-email course-status question omits necessary evidence. Since the holdout informed these changes, the 71/100 human score is intentionally unchanged pending a second unseen set.
