# TraceInbox Five-Minute Demo Recording Script

## Recording setup

- Record in 16:9 at 1080p. Keep your face visible throughout, as required by the course.
- Open `/presentation` first and the public TraceInbox demo in a second tab. Let Render wake up before recording.
- Use the left and right arrow keys to move through the introduction. The last scene opens the live demo.
- Use 90–100% browser zoom. Close personal tabs, notifications, password managers, and anything showing real email, API keys, `.env` values, or databases.
- Speak at roughly 125–135 words per minute. The target runtime is about five minutes.

## 0:00–1:38 — Dynamic introduction

### 0:00–0:20 — Scene 1: Title

**On screen:** Open `/presentation`. Stay on “From scattered messages to traceable decisions.”

**Say:**

> Hello, my project is TraceInbox, a privacy-aware email intelligence workspace. It turns scattered email messages into traceable decisions, while keeping the original messages visible as evidence. I built it for students and knowledge workers who receive deadlines, project updates, security notices and subscriptions across several inboxes.

### 0:20–0:48 — Scene 2: Why this project exists

**On screen:** Press the right arrow once.

**Say:**

> The problem is that one topic rarely lives in one email. A later message may change a deadline, routine subscription mail can look like a task, and forwarded university mail can hide the real sender. Normal inbox search can find keywords, but it does not reliably explain what changed, what still needs action, or which message supports the answer.

### 0:48–1:18 — Scene 3: Product workflow

**On screen:** Press the right arrow. Let the four workflow stages animate.

**Say:**

> TraceInbox uses a read-only workflow. It imports new messages incrementally, recovers original senders, runs deterministic security checks, and then uses DeepSeek or local Ollama for structured analysis. It extracts priorities, summaries, deadlines and action items. Related emails become knowledge topics, and the question-answering view retrieves local evidence before generating a cited answer.

### 1:18–1:38 — Scenes 4 and 5: Advantage and hand-off

**On screen:** Show the evaluation scene, then move to the final scene and select “Open TraceInbox demo.”

**Say:**

> The main advantage is traceability. Every important answer links back to source emails. The product is bilingual, supports multiple mailbox sources, and keeps security-critical state outside the model. I also report model failures rather than presenting the tuned regression score as production accuracy. Now I will demonstrate the complete public workflow using safe synthetic data.

## 1:38–4:27 — Live product walkthrough

### 1:38–2:05 — Demo entry and dashboard

**On screen:** Show the three sample accounts and display-only API key, then enter the demo and show the dashboard.

**Say:**

> The public version mirrors the real setup but cannot access a mailbox or external model. These three accounts and the API key are fictional and ignored. The demonstration imports 20 interrelated emails. The dashboard immediately shows processed mail, high-priority items, quarantined messages and the next actions, so the user can see what deserves attention before reading every email.

### 2:05–2:35 — Email detail and original-message link

**On screen:** Open one representative course or project email. Point to sender recovery, classification, summary, action and “Open original.” Briefly open the simulated original, then return.

**Say:**

> Each email keeps its recovered sender, received time, security result, classification, priority, bilingual summary and extracted action. Forwarded messages display the original sender instead of incorrectly showing the account owner. In a connected Gmail account, this button uses the exact Gmail thread ID. In the public demo it opens a simulated original, preserving the same end-to-end interaction without exposing personal data.

### 2:35–2:58 — Action items

**On screen:** Open “Action Items.” Show a deadline and the CloudNotes billing action. Mark one sample item complete only if you can immediately restore the demo state.

**Say:**

> Action items are generated only when the message requires a real user decision. Informational newsletters stay out of this view, while a failed payment or submission deadline remains visible. Reprocessing is idempotent, so it does not create duplicate tasks. Completing an item here also never changes or deletes the original email.

### 2:58–3:40 — Topic knowledge base

**On screen:** Open “Knowledge.” Select Project NOVA or the course topic and scroll through the grouped source emails.

**Say:**

> The knowledge page is more than another to-do list. It groups related messages into topics such as courses, projects, subscriptions, events and support cases. Opening a topic shows the messages that formed it in chronological context. This lets the user understand a continuing situation before asking a question, and it makes the system’s internal organization directly inspectable.

### 3:40–4:08 — Cross-email question answering

**On screen:** Open the Q and A view. Use a published demo question such as “What remains to be done for AX4102?” Point to the answer and its separate source list.

**Say:**

> For cross-email questions, relevant passages are retrieved locally. Only the selected evidence and question would be sent to the configured model in the full version. The answer combines the required repository, video, report, data and evaluation files, then cites the supporting email. The source list is deliberately separate from the prose so the user can verify every claim.

### 4:08–4:27 — Daily digest

**On screen:** Open “Daily Digest.” Point to urgent actions and concise updates.

**Say:**

> The daily digest compresses the mailbox into urgent actions and concise updates. Quarantined phishing content is excluded, and related actions use enough context to explain what must be done. This provides a quick morning view without replacing the underlying evidence.

## 4:27–5:00 — Evaluation and close

### 4:27–4:52 — Evaluation results

**On screen:** Return to presentation scene 4, or show the report’s evaluation chart.

**Say:**

> I evaluated the system with 20 transparent development emails, a separate frozen holdout, ten cross-email questions and 42 automated tests. In the real DeepSeek run, intent accuracy was 89.5 percent, priority accuracy 73.7 percent, and action accuracy 79 percent. Retrieval found the exact expected sources for all ten development questions, but only six answers were fully acceptable, and one legitimate security alert was wrongly described as phishing. This is the main reliability gap.

### 4:52–5:00 — Closing

**On screen:** End on the TraceInbox title or GitHub repository landing page.

**Say:**

> TraceInbox demonstrates a complete, privacy-safe and inspectable email workflow. The code, synthetic data, evaluation scripts, raw results, report and run instructions are all available in the GitHub repository. Thank you.

## Recording fallback notes

- If Render is sleeping, wait for it to wake before starting the recording; do not spend video time on the loading screen.
- If the question-answering page is slow, use the published example question and its existing auditable answer.
- Keep the path linear: **dashboard → message → action → topic → answer → digest → evaluation**.
- Do not explain every field. Narrate the user value, show the evidence, and move on.
- If the first take exceeds five minutes, shorten mouse movement and page scrolling before cutting evaluation or limitations.
