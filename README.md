# AI Email Agent

A bilingual, privacy-aware email workflow that turns an inbox into a traceable workspace. The application synchronizes Gmail or NetEase mail, evaluates security risk, classifies messages, extracts action items, organizes related emails into knowledge topics, and answers cross-email questions with source citations.

The project is built with Python, Flask, SQLite, IMAP, and either DeepSeek or a local Ollama model. English is the default course-delivery language; Chinese is available throughout the interface.

## What it demonstrates

- Reliable incremental IMAP synchronization without changing read status
- Forwarded-message normalization and original-sender recovery
- Deterministic security checks before model processing
- Multidimensional classification, priority, summaries, deadlines, and actions
- A local email knowledge index with stable content hashing and chunking
- Cross-email topic organization and cited retrieval-augmented answers
- Direct navigation back to the corresponding Gmail message when an exact thread ID is available
- A permanent welcome screen, onboarding import progress, dashboard, actions, knowledge, digest, and settings surfaces

## Safe public demo

The repository supports two deliberately separated modes:

| Mode | Data | Mailbox access | External model |
| --- | --- | --- | --- |
| Personal local mode | Your local mailbox data | Optional, configured locally | DeepSeek or Ollama |
| Public course demo | Five synthetic messages using reserved example domains | Disabled | Disabled |

Set `PUBLIC_DEMO=true` for a shareable deployment. Public demo mode automatically creates synthetic fixtures, hides account settings, disables mailbox synchronization and action mutations, and uses an extractive local answer path. It never needs a mailbox credential or API key.

Never commit `.env`, `data/`, or a SQLite database. They are excluded by both `.gitignore` and `.dockerignore`.

## Architecture

```text
IMAP / demo fixture
       │
       ▼
Security gate → Triage → Action extraction
       │                    │
       ▼                    ▼
  SQLite audit log      Action workspace
       │
       ▼
Incremental knowledge chunks → Topic organization → Local retrieval → Cited answer
```

Key modules:

- `app/email_client.py` — read-only IMAP and incremental UID synchronization
- `app/security.py` — deterministic risk signals and quarantine decision
- `app/triage.py` — validated structured model output
- `app/actions.py` — idempotent action-item generation
- `app/knowledge.py` — stable local document and chunk indexing
- `app/topics.py` — deterministic cross-email topic organization
- `app/rag.py` — local retrieval, bounded context, answers, and citations
- `app/main.py` — Flask routes and bilingual server-rendered UI
- `app/demo_seed.py` — synthetic public-demo dataset

More detail is available in [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY_PRIVACY.md](SECURITY_PRIVACY.md), and [docs/THREE_DAY_EXECUTION_BASELINE.md](docs/THREE_DAY_EXECUTION_BASELINE.md).

## Run the safe demo with Docker

```bash
docker compose up --build
```

Open <http://127.0.0.1:8000>. Docker starts the application with `PUBLIC_DEMO=true`; no secrets are required.

## Run locally for personal use

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open <http://127.0.0.1:8000>, connect a mailbox with an app password, and choose the size of the first import. Credentials and email content stay in the ignored local SQLite database. If DeepSeek is configured, selected email content is sent to that API for analysis. Without a DeepSeek key, the application uses the configured local Ollama service.

## Configuration

The checked-in `.env.example` contains empty placeholders only.

| Variable | Purpose | Public demo value |
| --- | --- | --- |
| `PUBLIC_DEMO` | Enforces synthetic read-only deployment behavior | `true` |
| `DEMO_MODE` | Uses demo rather than IMAP fetch behavior | `true` |
| `DEEPSEEK_API_KEY` | Optional personal cloud-model key | unset |
| `OLLAMA_BASE_URL` | Optional local model endpoint | unset in cloud demo |
| `IMAP_USER` / `IMAP_PASSWORD` | Optional personal mailbox connection | unset |
| `HOST` / `PORT` | Local server binding | `0.0.0.0` / `8000` in Docker |

## Tests

```bash
python -m unittest discover -s tests -v
```

The regression suite covers migrations, incremental synchronization, forwarded senders, Gmail links, triage validation, action idempotency, knowledge indexing, topic grouping, retrieval precision, bilingual UI behavior, and public-demo isolation.

## Deploy on Render

The included `render.yaml` and `Dockerfile` define a safe public demo:

1. Push this repository to GitHub.
2. In Render, create a new Blueprint and select the repository.
3. Render reads `render.yaml`, builds the Docker image, and exposes `/health` for health checks.
4. Do not add mailbox credentials or model API keys to the public demo.

Render's free service may sleep when inactive and take a short time to wake up.

## Privacy boundary

- The application never sends or replies to email automatically.
- Public demo mode cannot connect to a mailbox or edit account settings.
- Runtime databases and secrets are excluded from Git and Docker build context.
- The public fixture uses only synthetic content and reserved example domains.
- Personal mode is intended to run on the user's computer unless a private, authenticated deployment is added later.

## License

[MIT](LICENSE)
