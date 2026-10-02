# TraceInbox Security and Privacy Model

## Protected data

TraceInbox treats mailbox app passwords, model API keys, session secrets, email content, contacts, derived summaries, source links, logs, and databases as sensitive. Derived data can reveal the meaning of source mail and therefore receives the same protection as email content.

| Class | Examples | Required handling |
|---|---|---|
| Secrets | Mailbox app password, API key, session/encryption keys | Never log or display; encrypt at rest where stored |
| Private content | Messages, contacts, source links | Keep local by default; minimize before cloud processing |
| Derived content | Summaries, classifications, actions, digest | Protect as private content |
| Operational data | Timing, error type, model version | May be logged without secrets or full message text |

## Privacy modes

**Public course demo.** Uses only 20 synthetic messages with fictional identities. Mailbox synchronization, external model calls, settings mutations, and real provider navigation are disabled or simulated.

**Personal local mode.** Stores the workspace locally. Ollama keeps model inference on the user's computer. IMAP still communicates with the selected mailbox provider.

**DeepSeek-enhanced mode.** Sends only the email fields required for analysis to the user's configured DeepSeek endpoint. The interface discloses this data flow before use.

**Hosted multi-user prototype.** Requires authentication, binds every request and background import to one account, isolates workspace databases, hashes login passwords, and encrypts mailbox/model credentials at rest. It is not presented as production-ready hosting.

## Trust boundaries and controls

| Threat | Implemented or required control | Remaining risk |
|---|---|---|
| Secret disclosure | Ignored `.env`/databases, encryption, password hashing, redacted errors | A fully compromised host can still expose runtime secrets |
| Unauthorized hosted access | Login, CSRF protection, secure cookie options, tenant binding | Stolen sessions remain usable until expiry |
| Prompt injection in email | Treat email as untrusted data, deterministic tool boundary, structured outputs | Language models may still make semantic mistakes |
| Malicious links and HTML | Do not execute raw HTML; deterministic risk signals; provider-generated source links | Sanitizers and provider URL formats require maintenance |
| Duplicate processing or cost | Account + provider UID/message identity and idempotent writes | Missing provider identifiers require stable fingerprints |
| Oversized input | Limits for body, batch, context, and model tokens | Legitimate large messages may be truncated |
| Cross-tenant access | Request-scoped workspace binding and job ownership checks | Production deployment still needs an independent security audit |
| Ephemeral cloud storage | Public demo is reproducible; personal data should remain local | Free Render storage is not durable |

## Untrusted-content rules

- Subject, body, sender name, HTML, attachment names, links, and forwarded content are data, never instructions to the application.
- Email content cannot authorize reading secrets, changing configuration, running commands, or adding tools.
- Deterministic security checks run before semantic classification.
- The model may raise risk but cannot override a deterministic quarantine decision.
- Original-message links are constructed from trusted provider identifiers or simulated inside the public demo.
- Logs must not include credentials, authorization headers, or complete private bodies.

## Repository and deployment safety

- `.env`, `data/`, SQLite files, credentials, and runtime artifacts are excluded from Git and Docker build context.
- `.env.example` contains placeholders only.
- The public deployment must use `PUBLIC_DEMO=true` and must not receive real mailbox or model credentials.
- Personal mode should run locally unless a private deployment has durable encrypted storage and appropriate operational controls.

## Remaining production work

Before real public use, add managed durable storage, account-level export/deletion, login throttling, key rotation, stronger SSRF controls for any future web retrieval, dependency monitoring, security telemetry, backup policy, and an independent penetration/security review.
