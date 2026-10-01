# AI Email Agent: From Inbox Noise to Traceable Action

## Problem and intended user

Email is not merely a message list. For a student or early-career professional, one inbox may contain course deadlines, project decisions, account warnings, subscriptions, recruitment opportunities, forwarded institutional mail, and personal conversations. Important facts are often spread across several messages, and later emails may supersede earlier instructions. Conventional inbox search can locate words, but it does not reliably answer questions such as “What remains for this course?” or “Which subscription actually needs action?”

This project builds a bilingual, privacy-aware Email Agent for an individual user. It converts read-only mailbox content into security decisions, multidimensional classifications, concise summaries, action items, cross-email topics, a daily digest, and cited question answering. The original email remains the source of truth, and the product links back to it whenever the provider identifier permits.

## Product outcome

The implemented Flask application supports Gmail and NetEase through incremental IMAP retrieval; forwarded Outlook or university messages can be normalized inside Gmail. A first-use flow asks for the mailbox and import limit, while later synchronization fetches only newer messages. Each message passes through deterministic security checks before optional DeepSeek or local Ollama analysis. Results are stored in SQLite and presented through an English-first interface with a Chinese language option.

The workflow produces more than a flat to-do list. Related emails are organized into topics such as a course, project, subscription, event, support case, or correspondent. The knowledge page retrieves relevant evidence across messages and displays citations. Informational subscriptions are excluded from actions, but an urgent failed subscription payment can still become an action. Public deployment uses 20 entirely synthetic messages and disables real mailbox and external-model access.

## Architecture and reasoning

The high-level transformation is:

```text
IMAP or synthetic fixture
        ↓
Normalization and deduplication
        ↓
Deterministic security gate
        ↓
Structured LLM triage (DeepSeek or Ollama)
        ↓
SQLite audit record, actions, and knowledge chunks
        ↓
Topic organization → retrieval → cited answer and daily digest
```

I deliberately separated deterministic responsibilities from probabilistic intelligence. UID cursors, MIME parsing, forwarding identity, timestamps, hashes, idempotency, security thresholds, and source links are code-controlled because failures here would corrupt state or trust. The model handles semantic classification, summarization, and action suggestions, but its structured output is validated before persistence. This design is less flexible than an unrestricted agent, yet it is easier to inspect, test, and explain.

## Business and technical trade-offs

The main business trade-off is convenience versus privacy. DeepSeek offers accessible cloud inference, but selected email content leaves the device. Ollama keeps content local but requires suitable hardware and can be slower. The interface therefore makes the model choice explicit rather than silently failing over across privacy boundaries.

IMAP with app passwords was chosen over Gmail and Microsoft OAuth for the prototype because it reduced integration time and supported multiple providers. The cost is weaker consumer onboarding and no native Outlook connection. Similarly, SQLite makes the local version portable and transparent, but a serious hosted multi-user product should use managed persistent storage, stronger operational monitoring, and provider OAuth.

The Render deployment is intentionally a safe demonstration rather than a production mailbox service. Visitors see realistic input fields and full product navigation, but the values are ignored and all messages use reserved fictional domains. This sacrifices live personalization in exchange for reproducibility and zero exposure of personal email or API credentials.

## Evaluation design and results

The checked-in development set contains 20 synthetic but realistic messages and 10 cross-email questions. It covers updated deadlines, completed tasks, multi-source changes, subscription distinctions, phishing isolation, support resolution, optional career events, and unsupported questions. Automated tests also cover synchronization, migration, sender recovery, original-message links, idempotency, multi-user isolation, bilingual routing, public-demo safety, indexing, and retrieval.

After tuning, the fixed regression set reached 100% topic accuracy, action precision/recall, retrieval precision/recall, exact source sets, and unsupported-question abstention. This number is not an unbiased accuracy estimate: the same cases informed the rule changes, and gold per-message labels bypass model classification.

A separately frozen first-run holdout used 10 unseen messages and five questions. It exposed the real weakness: strict topic-key accuracy was only 10%, although retrieval achieved 87.5% precision, 100% recall, and 80% exact source sets. The unsupported hotel question also failed to abstain. General topic extraction and refusal filtering were then improved, but that rerun is reported only as regression evidence because the holdout had become known.

A subsequent real-DeepSeek run used the synthetic set without exposing gold answers to the model. Intent accuracy was 89.5%, priority accuracy 73.7%, action-decision accuracy 79.0%, and exact deadline accuracy 73.7%. Retrieval returned the exact expected source set for all ten questions, yet only six answers were fully acceptable in author review: three omitted required facts and one incorrectly labelled a legitimate security alert as phishing. Median answer latency was 40.9 seconds. These results show why retrieval and answer quality must be reported separately.

## Difficulties, critique, and tuning

The hardest problems were not page construction or API calls. They were identity recovery from forwarded messages, accurate provider links, preventing duplicate actions after reprocessing, separating an informational subscription from an urgent billing failure, and retrieving later updates without citing unrelated keyword matches.

Early retrieval returned unrelated Google subscription messages for a course question. Exact identifiers were changed into hard filters, stopwords and query-only expansions were added, and confidence thresholds were tightened. Early topic logic also overfit named cases such as AX4102 and Project NOVA. The first holdout revealed this clearly, leading to generic recognition of course codes, `Project + name`, provider subscriptions, and event types. One known multi-email holdout question still omits necessary evidence after the stricter threshold, demonstrating the precision–recall tension.

The product remains a prototype. The public demo uses reproducible checked-in answers, while the separate model run exposes incomplete and occasionally contradictory generation. There is no blind second holdout, attachment understanding, production security audit, large-mailbox load test, or longitudinal user study. Render's free filesystem is ephemeral, so hosted persistence is not guaranteed without managed storage.

## Future path

The next evaluation should freeze a second unseen multilingual set and have an independent reviewer rescore the saved model answers for completeness, claim-level citation faithfulness, and refusal quality. Product improvements should add provider OAuth, managed encrypted storage, vector-plus-lexical retrieval, attachment parsing, user corrections, latency and cost telemetry, and calibrated confidence. These steps would move the project from a persuasive course demonstration toward a trustworthy personal information system.
