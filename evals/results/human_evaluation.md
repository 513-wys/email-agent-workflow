# Simulated Independent Human Evaluation

Evaluation date: 1 October 2026  
Evaluated artifact: `email-agent-public-demo-v2`  
Rubric: `evals/HUMAN_EVAL_RUBRIC.md`

## Executive result

**Overall score: 76/100 — Credible prototype**

The system demonstrates a coherent, privacy-safe email workflow and a reproducible evaluation harness. Its strongest evidence is deterministic organization, action handling, source traceability, and public-demo isolation. Its largest weakness is that the reported 100% final regression score was obtained on the same 20 emails and 10 questions used to tune the rules. The public demo's answer path is extractive rather than a separately evaluated synthesis model, and no unseen or adversarial holdout set has yet been scored.

## Scorecard

| Dimension | Score | Weight | Reviewer evidence and deductions |
| --- | ---: | ---: | --- |
| Task correctness | 17 | 20 | The fixed set now correctly groups topics and handles actions, deadlines, completion, and quarantine. Deducted because the run injects gold per-message labels and therefore does not measure model classification quality. |
| Answer completeness and usefulness | 13 | 20 | The 10 questions specify strong content expectations, including superseded facts and multi-email synthesis. However, the offline runner scores source sets rather than the wording, completeness, or readability of generated answers; public-demo answers are extractive snippets. |
| Retrieval relevance | 14 | 15 | All expected source sets pass after tuning. Deducted because evaluation and tuning use the same set and some retrieval logic contains domain-specific lexical rules. |
| Citation faithfulness and traceability | 8 | 10 | Retrieved emails are exposed as sources and answers use numbered citations. Deducted because claim-level citation correctness has not been independently annotated or scored. |
| Safety and privacy | 9 | 10 | Public data uses reserved fictional domains; the phishing case is quarantined; unsupported questions abstain; demo mode disables mailbox/API access. Deducted because a synthetic demo and unit tests are not a production penetration/security audit. |
| Robustness and generalization | 4 | 10 | Identifier hard filters and regression tests address known failures. Major deductions: no held-out email set, no paraphrase suite, limited bilingual RAG evaluation, no large-mailbox/load test, and possible overfitting to AX4102/NOVA/subscription wording. |
| UX and demo readiness | 4 | 5 | The application has an English-first demo, Chinese switch, onboarding, dashboard, knowledge, actions, digest, and simulated original-email view. Deducted because a complete moderated user test and final 20-message deployed walkthrough have not yet been documented. |
| Reproducibility and transparency | 7 | 10 | Dataset, expected labels, QA set, executable runner, baseline, final results, comparison, README, product documentation, and architecture are checked in. Deducted because there is no model-backed result file, human annotation sheet, environment/version manifest, or held-out result yet. |
| **Total** | **76** | **100** | **Credible prototype; not a production-quality or generalized 100% system.** |

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

For the report, the defensible claim is: **“The tuned deterministic layer achieved 100% on the fixed regression set; a rubric-based simulated human audit scored the overall prototype 76/100, with generalization and generated-answer evaluation as the principal gaps.”**

## Required next evidence

1. Freeze the current 20 cases as the development/regression set.
2. Create a separate held-out set of at least 10 emails and 5 paraphrased questions that are not used during tuning.
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
| Targeted metrics and reached metrics | Baseline/final comparison plus human score | Present, but held-out/model-backed metrics remain missing |

This checklist should be updated again immediately before submission.
