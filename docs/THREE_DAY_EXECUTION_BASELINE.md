# Three-Day Execution Baseline — Historical Planning Record

This document records the compressed implementation baseline used to move TraceInbox from an early Flask email viewer to the current product prototype. It is retained for process transparency. It is not the current status report; use the repository `README.md`, saved evaluation results, and current tests for final evidence.

## Starting point

At the start of the three-day plan, the repository already had a Chinese Flask interface, manual mail fetching, DeepSeek/Ollama calls, single-message summaries, and a basic SQLite database. It did not yet have reliable incremental synchronization, robust forwarded-sender recovery, dynamic action items, multidimensional classification, a stable knowledge index, cross-email retrieval, citations, or dependable original-message navigation.

## Product definition

The planned product was a local-first, read-only email agent for students and knowledge workers. It would turn incoming mail into a safe, traceable working view while preserving the source mailbox as the authority. The product would provide equivalent English and Chinese interfaces.

Key outputs were prioritized email, security decisions, bilingual summaries, actions and deadlines, related-message topics, cited cross-email answers, a daily digest, and a route back to the original evidence.

## Architecture baseline

```text
Mailbox / synthetic fixture
        |
        v
Read-only import -> normalization -> deterministic security gate
        |                                  |
        v                                  v
provider identity                     quarantine evidence
        |
        v
structured triage -> actions -> SQLite audit/workspace
        |
        v
stable knowledge chunks -> topic grouping -> retrieval -> cited answer
```

Deterministic code owns protocol behavior, identity, dates, deduplication, state, links, security thresholds, persistence, and retrieval boundaries. Models own language understanding and generation, subject to normalization and bounded context.

## Planned task coordinates

| Track | Scope |
|---|---|
| A | Product scope, architecture, contracts, and privacy boundary |
| B | Model gateway, structured prompts, and validation |
| C | Account configuration and provider connection |
| D | UID sync, time handling, MIME/forward parsing, deduplication, links |
| E | Security signals and quarantine |
| F | Classification, summaries, priority, deadlines, and actions |
| G | Knowledge indexing, topics, retrieval, answers, citations |
| H | Database migrations, orchestration, progress, and isolation |
| I | Welcome/onboarding, dashboard, detail, actions, knowledge, digest, settings |
| J | Fixtures, tests, evaluation, performance, and reviewer evidence |
| K | Secret handling, safe deployment, documentation, and release checks |

## Three-day order

### Day 1 — reliable evidence pipeline

1. Freeze product scope and data contracts.
2. Add provider-UID incremental synchronization and safe bounded first import.
3. Normalize dates and forwarded messages; recover original senders.
4. Generate trusted provider links and deterministic security evidence.
5. Add migrations and tests for identity, deduplication, and parsing.

### Day 2 — understanding and organization

1. Expand structured triage into intent, priority, summaries, action decisions, and deadlines.
2. Make action creation idempotent.
3. Build content-hashed knowledge documents and chunks.
4. Group related messages by stable course, project, support, subscription, security, career, and event keys.
5. Add local retrieval, bounded model context, and numbered citations.

### Day 3 — product flow and evidence

1. Finish onboarding/import progress and the English/Chinese interface.
2. Create the public synthetic demo and deployment boundary.
3. Validate dashboard, details, actions, topics, QA, digest, and original-message simulation.
4. Check in transparent fixtures, holdout cases, evaluation runners, saved metrics, and failure analysis.
5. Complete README, architecture, privacy documentation, and reproducible demo guidance.

## Final demonstration acceptance criteria

- A reviewer can open a safe English demo without credentials.
- The demo contains 20 coherent, representative, fictional messages with related threads.
- The dashboard surfaces priority and security state.
- A detailed message shows sender recovery, summary, classification, action, and evidence navigation.
- Topic pages group only related messages in a useful order.
- Cross-email questions return concise answers with relevant, openable citations and abstain when evidence is insufficient.
- The daily digest distinguishes urgent actions from informational updates.
- The repository explains how to run both the safe demo and the personal local version.
- Data, evaluation design, raw/summarized results, targets, failures, and limitations are visible in the repository.
- No real mailbox data, password, API key, database, or personal identifier is required for course review.

## Outcome

The final repository implements the planned end-to-end flow and preserves its evaluation evidence. It also records important limitations: small datasets, known-set overfitting risk, imperfect real-model triage, one security-answer contradiction in model evaluation, slow model-backed QA, IMAP rather than OAuth, lexical rather than hybrid retrieval, and non-durable free-tier cloud storage.
