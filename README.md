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

## Deployment modes

The repository supports two deliberately separated modes:

| Mode | Data | Mailbox access | External model |
| --- | --- | --- | --- |
| Personal local mode | Your local mailbox data | Optional, configured locally | DeepSeek or Ollama |
| Public course demo | Curated synthetic messages using reserved example domains | Disabled | Disabled |
| Hosted multi-user mode | Separate workspace database for each account | Each user supplies their own mailbox credential | Each user supplies their own DeepSeek key |

Set `PUBLIC_DEMO=true` for a shareable deployment. Visitors first see a display-only setup form prefilled with fictional email and API values. Submitting it stores nothing and opens a synthetic workspace. Public demo mode hides account settings, disables mailbox synchronization and action mutations, and uses an extractive local answer path. It never needs a mailbox credential or API key.

Set `MULTI_USER_MODE=true` and `PUBLIC_DEMO=false` for the hosted application. Visitors register before they can access any workspace route. Account passwords are salted and hashed; mailbox credentials and DeepSeek keys are encrypted before storage; email, actions, knowledge, sync cursors, and settings live in a separate database per account. The hosted prototype uses Gmail/NetEase app passwords rather than collecting the user's normal sign-in password.

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
- `app/auth.py` — hosted account registration, password verification, and CSRF tokens
- `app/tenant.py` — request/background-job workspace isolation
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
| `MULTI_USER_MODE` | Requires accounts and isolates hosted workspaces | `false` |
| `APP_SECRET_KEY` | Signs browser sessions; use a long random production value | unset |
| `APP_ENCRYPTION_KEY` | Encrypts each user's mailbox credential and model key | unset |
| `COOKIE_SECURE` | Sends hosted session cookies only over HTTPS | `false` locally |
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

The included `render.yaml` and `Dockerfile` define the safe public course demo:

1. Push this repository to GitHub.
2. In Render, create a new Blueprint and select the repository.
3. Render reads `render.yaml`, builds the Docker image, and exposes `/health` for health checks.
4. Visitors enter through a fictional, prefilled setup screen. The submitted display values are ignored; no mailbox or external model is contacted.

To deploy the authenticated multi-user mode instead, set `PUBLIC_DEMO=false`, `DEMO_MODE=false`, and `MULTI_USER_MODE=true`, then provide persistent encrypted storage before inviting real users.

Render's free service may sleep when inactive and take a short time to wake up.

## Privacy boundary

- The application never sends or replies to email automatically.
- Public demo mode cannot connect to a mailbox or edit account settings.
- Hosted mode requires authentication and uses a separate workspace database per user.
- Mailbox credentials and DeepSeek keys are encrypted at rest and never shown back to the browser.
- Runtime databases and secrets are excluded from Git and Docker build context.
- The public fixture uses only synthetic content and reserved example domains.
- The free Render filesystem is ephemeral. A production deployment must attach persistent encrypted storage or migrate workspaces to a managed database before promising durable retention.

## License

[MIT](LICENSE)
