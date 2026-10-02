# TraceInbox Implementation Plan and Status Map

This file preserves the project's implementation coordinates in a concise English form. It is a planning/status artifact, not the primary reviewer entry point. For the final product state, start with [`README.md`](README.md), the saved results in [`evals/results/`](evals/results/), and the current code.

## Product boundary

TraceInbox is a read-only email intelligence workspace. It imports Gmail or NetEase mail, handles forwarded institutional/Outlook messages, performs security screening and semantic triage, extracts actions, organizes cross-email topics, creates a digest, and answers questions with citations. It supports English and Chinese interfaces, a local DeepSeek/Ollama path, an authenticated hosted prototype, and a safe synthetic public demo.

It does not send, delete, archive, or automatically reply to email. Native Outlook OAuth, attachment understanding, and production-grade cloud storage are outside v1.

## Work coordinates

| Area | Coordinate range | Intended outcome | Final state |
|---|---|---|---|
| Product and architecture | A-01–A-05 | Scope, deterministic/model boundary, contracts, threat model | Complete |
| Model and prompts | B-01–B-11 | DeepSeek/Ollama gateway, structured triage, safe prompting | Implemented; model-quality limitations evaluated |
| Mailbox access | C-01–C-06 | Gmail/NetEase setup, account state, encrypted credentials | Implemented for prototype use |
| Import and normalization | D-01–D-11 | Read-only UID sync, parsing, sender recovery, deduplication, links | Implemented and regression tested |
| Security gate | E-01–E-07 | Deterministic signals, quarantine, safe evidence | Implemented; production hardening remains |
| Triage and actions | F-01–F-09 | Intent, priority, bilingual summaries, deadlines, actions | Implemented and evaluated |
| Context and knowledge | G-01–G-07 | Stable index, topics, retrieval, cited answers | Implemented and evaluated |
| Persistence and orchestration | H-01–H-06 | Schema migration, auditability, isolation, background progress | Implemented for local/prototype scale |
| User interface | I-01–I-10 | Welcome/onboarding, dashboard, details, actions, knowledge, digest | Complete in English and Chinese |
| Testing and evaluation | J-01–J-08 | Synthetic data, holdout, model eval, performance and human rubric | Complete with saved evidence |
| Privacy and release | K-01–K-10 | Secret exclusion, CSRF/auth, tenant isolation, safe demo | Complete for course delivery; production gaps documented |

## Key milestones

1. **Reliable ingestion:** moved from manual/simple fetching to bounded first import and incremental provider-UID synchronization without changing read state.
2. **Traceable analysis:** added deterministic security signals, structured triage, bilingual summaries, priority, deadline, and source-aware actions.
3. **Cross-email organization:** added content-hashed indexing, topic pages, retrieval, citations, and direct/simulated original-message navigation.
4. **Usable product flow:** added a permanent welcome screen, onboarding configuration, import progress, dashboard, email detail, actions, knowledge, digest, and settings.
5. **Safe delivery:** separated local/full functionality from a 20-message public demo and added authentication/isolation for the hosted prototype.
6. **Transparent evaluation:** checked in fixtures, frozen holdout cases, evaluation runners, raw/summarized results, a human scoring rubric, and failure analysis.

## Verification evidence

| Claim | Evidence |
|---|---|
| Product can be reviewed without credentials | `PUBLIC_DEMO=true`, Docker configuration, live Render demo |
| Demo data are transparent and fictional | `fixtures/demo_email_cases.json`, `fixtures/README.md` |
| Known-set and held-out behavior are measured separately | `evals/run_final.py`, `evals/run_holdout.py`, saved result files |
| Real model quality is not presented as perfect | `evals/results/model_evaluation.md`, human semantic review |
| Software behavior is regression tested | `tests/` and the test command in `README.md` |
| Privacy boundaries are explicit | `SECURITY_PRIVACY.md`, `.gitignore`, `.dockerignore`, `.env.example` |
| Architecture and contracts are inspectable | `ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md`, `schemas/` |

## Remaining future work

- Provider OAuth and native Microsoft Graph integration
- Durable managed database and background queue for real hosted use
- Account export/deletion, login throttling, key rotation, and independent security review
- Attachment extraction with strict size/type controls
- Hybrid lexical/vector retrieval and a larger untouched multilingual evaluation set
- Cost and latency telemetry, correction feedback, and calibrated confidence

These items are explicitly future work and are not claimed as completed course-delivery functionality.
