# TraceInbox Data Contracts

The machine-readable baseline is [`schemas/email_agent_contracts.schema.json`](../schemas/email_agent_contracts.schema.json). This document explains the domain objects and migration rules used by the application.

## Domain objects

| Object | Purpose | Key fields |
|---|---|---|
| `MailAccount` | Mailbox configuration and sync state | provider, email, secret reference, enabled, last sync |
| `EmailEvent` | Stable provider event | account, UID/source ID, message ID, thread ID, internal date |
| `NormalizedEmail` | Parsed content | sender, original sender, recipients, subject, text/HTML, forward chain |
| `SecurityAssessment` | Deterministic/model risk result | score, level, safe flag, signals, reasons |
| `TriageResult` | Semantic analysis | intent, priority, confidence, summaries, actions, deadline |
| `ContextBundle` | Supporting context | contact, company, references, source URLs |
| `ProcessingRun` | Import audit record | state, start/end, counts, errors |
| `CorrectionRecord` | User feedback | previous result, replacement, reason, timestamp |
| `DigestReport` | Daily aggregation | date, totals, distribution, actions, items |

## Contract rules

- Identifiers are stable opaque strings; timestamps use timezone-aware RFC 3339 values; account time zones use IANA names.
- Stored enums are stable English values. The presentation layer supplies English and Chinese labels.
- Raw email HTML is untrusted input and must never be executed directly.
- Secret fields store references or encrypted values, never plaintext values intended for display.
- Model output must be normalized and validated before persistence.
- Unknown classifications use `OTHER`; runtime code must not invent new enum values.

## Migration rules

1. The contract baseline is versioned. Adding optional fields is a minor change; removing, renaming, or changing semantics is a major change.
2. SQLite records applied migrations with version, timestamp, and checksum.
3. Each migration supplies forward changes, data backfill behavior, and compatibility notes.
4. Application startup applies missing migrations before normal writes and fails safely if a migration cannot complete.
5. Legacy records are backfilled from provider IDs and stored timestamps when possible. Unknown values remain explicitly unknown rather than being replaced with the current time.

## Persistence mapping

| Stored concept | Contract mapping |
|---|---|
| Provider UID | `EmailEvent.source_id` |
| RFC Message-ID | `EmailEvent.message_id` |
| Provider thread/message identifier | Original-message navigation fields |
| Parsed sender and forwarded sender | `NormalizedEmail.from` / `original_from` |
| Stable classification | `TriageResult.intent` |
| Import trace and errors | `ProcessingRun` |
| Knowledge document/chunks | Derived index keyed by normalized email and content hash |
