# Synthetic Demo Dataset

`demo_email_cases.json` is the canonical, privacy-safe dataset for the public course demo.

- Every person, account, organization, identifier, and message is fictional.
- Reserved domains (`example.com`, `example.org`, `example.edu`, and `.invalid`) prevent accidental delivery.
- The 20 messages intentionally form related topic clusters so classification, action extraction, topic grouping, retrieval precision, and citations can be evaluated together.
- `expected` fields are labels, not model inputs. They define the acceptance target for deterministic fixtures and evals.

The public demo should preserve the wording and identifiers that make each case testable, especially `AX4102`, `Project NOVA`, `SEC-4821`, and `CS-1047`.
