# TraceInbox Product Definition

## Product summary

TraceInbox is a bilingual, privacy-aware email intelligence workspace. It can run on a personal computer or as an authenticated multi-user prototype. English is the default interface; Chinese provides equivalent functionality.

The product converts email into a traceable workflow: it imports messages, recovers original senders from forwarded mail, checks deterministic security signals, classifies and summarizes content, extracts action items, groups related messages into topics, produces a daily digest, and answers cross-email questions with source citations.

## Primary persona

The primary user is a student or knowledge worker managing course, project, subscription, security, support, career, and event messages across one or more addresses. The user wants concise decisions without losing access to the original evidence.

## Inputs and outputs

**Inputs**

- Gmail or NetEase mail through read-only IMAP
- Outlook or institutional mail forwarded to a connected mailbox
- A personal DeepSeek API key or a local Ollama endpoint
- The checked-in synthetic fixture in public-demo mode

**Outputs**

- Prioritized and categorized email views
- English and Chinese summaries
- Extracted action items and deadlines
- Cross-email topic pages
- Cited question answering
- A daily digest
- Provider or simulated-original-message links

## v1 scope

The implemented scope includes mailbox onboarding, configurable first import, incremental synchronization, sender recovery, security screening, multidimensional triage, summaries, actions, knowledge indexing, topic grouping, cited retrieval, digest generation, English/Chinese switching, and separate local, hosted, and safe-demo modes.

The product deliberately does not send, delete, archive, or automatically reply to email. Native Outlook OAuth, attachment understanding, provider OAuth, vector retrieval, and production-grade managed storage remain future work.

## Product principles

1. **The source mailbox remains authoritative.** TraceInbox presents derived analysis and always preserves a route back to evidence.
2. **Deterministic operations precede model judgment.** Authentication, dates, deduplication, links, security thresholds, and persistence are controlled by code.
3. **Content determines meaning.** Sender domains are useful signals but do not replace semantic analysis.
4. **Failures degrade locally.** One failed message or model call must not break the whole import.
5. **Privacy choices are explicit.** The interface distinguishes cloud-model processing from local inference.
6. **Advice is separated from action.** The model can recommend and summarize, but it does not perform external email actions.
7. **Evidence is visible.** Cross-email answers include openable sources, and uncertain results should be stated as uncertain.

## Deployment modes

| Mode | Mailbox data | Model | Intended use |
|---|---|---|---|
| Public course demo | 20 synthetic messages | Reproducible local answers | Safe review and presentation |
| Personal local | User-controlled local database | DeepSeek or Ollama | Individual use |
| Hosted multi-user prototype | Per-account isolated workspace | User-supplied encrypted credentials | Experimental shared deployment |

## Success criteria

- A reviewer can run the safe demo without secrets.
- A personal user can import mail without changing read status.
- Forwarded messages show the original sender when recoverable.
- Important actions and deadlines are easy to scan.
- Related messages can be inspected as one topic.
- Cross-email answers cite only relevant sources.
- The repository exposes its data, evaluation method, targets, reached metrics, and known failures.

## Known limitations

- IMAP app passwords are less convenient than OAuth.
- SQLite is appropriate for local use but Render's free filesystem is not durable production storage.
- Lexical retrieval is transparent and strong for identifiers, but weaker for paraphrases than hybrid retrieval.
- The synthetic and holdout datasets are small, and the model-backed evaluation found incomplete answers, a security contradiction, and slow QA latency.
- A production release would still require durable storage, deletion controls, login rate limiting, key rotation, broader security testing, and a larger multilingual holdout.
