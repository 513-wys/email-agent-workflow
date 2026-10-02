# TraceInbox Five-Minute Demo Script

## Recording setup

- Record at 16:9, 1080p, with face and computer screen visible throughout.
- Open `/presenter`. Its compact upper area is the private teleprompter; the lower area contains the presentation and product demo.
- Crop the recording to the area below the marked share line so the teleprompter is not captured.
- Use `Start timer` for the five-minute clock and `A−` / `A+` to adjust prompt size.
- Wake the Render service and verify the demo before recording.
- Keep browser zoom at 90–100%. Close notifications, private tabs, real mail, API keys, `.env`, and database views.
- Use the left/right arrow keys for the animated introduction.
- The spoken script is approximately 620–650 words; use a natural pace.

---

## 0:00–1:25 — Introduction

### 0:00–0:22 — Slide 1: open with a real scenario

**Action:** Open `/presenter` on the first title slide. Face the camera for the first two questions, then turn attention to the title at “TraceInbox is my answer.”

**Say:**

> Imagine opening your inbox and seeing a deadline, a project update, a payment problem, and a security alert together. Which one needs attention first? Which email has the latest information? TraceInbox is my answer. It turns scattered emails into clear actions, connected topics, and answers with sources.

### 0:22–0:43 — Slide 2: define the problem

**Action:** After “answers with sources,” press the right arrow once. Point to the first example card at “several messages.”

**Say:**

> That is why I built TraceInbox. Email is easy to receive, but hard to organize. One task may be spread across several messages. A later email may change a deadline, and forwarding may hide the real sender. Search finds messages, but not the full story.

### 0:43–1:06 — Slide 3: explain the workflow

**Action:** Press right after “not the full story.” Follow the highlighted Import, Triage, Organize, and Answer stages.

**Say:**

> So how does it turn that messy inbox into something useful? TraceInbox imports new emails, checks security, and finds the original sender. It then creates actions and groups related messages into topics. Finally, it searches the local knowledge base and answers questions with links to the source emails.

### 1:06–1:18 — Slide 4: advantage and evaluation

**Action:** Press right and remain for about 12 seconds. Point to “Evidence before confidence,” then to the evaluation figures.

**Say:**

> Before the live demo, this page shows the main advantage: traceability. Every action and answer links back to an original email. The evaluation also shows the system's limits.

### 1:18–1:25 — Slide 5: transition

**Action:** Press right after “system's limits,” deliver the line, then click `Open TraceInbox demo`.

**Say:**

> With that idea in mind, let us move from the overview to the live product.

---

## 1:25–4:30 — Operate and explain the product

### 1:25–2:00 — Welcome page and first import

**Actions:** Point to Connected mailbox, additional owned/forwarding addresses, API/model choice, and first-import count. Then start the demo import.

**Say:**

> This is the first page a new user sees. Here, I enter the main mailbox I want to connect. I can also add other addresses that belong to me. For example, I may forward my university email into Gmail. TraceInbox reads the forwarding information and shows the original sender, not my own address.
>
> I can choose DeepSeek or a local Ollama model, and choose how many recent emails to import. The default is one hundred. In this demo, all values are fictional and nothing is saved or sent outside the app. I will now start the import.

### 2:00–2:25 — Import progress and dashboard

**Actions:** Briefly show progress. On the dashboard, point to Emails processed, High priority, Quarantined, and Next actions.

**Say:**

> During the first import, I can see the progress instead of waiting on a blank page. This demo loads twenty connected emails. The dashboard then shows the processed emails, urgent items, quarantined messages, and my next actions. I can understand the situation before opening every message.

### 2:25–2:58 — Email detail and source navigation

**Actions:** Open Emails, select a representative AX4102 course message, point to sender/category/priority/summaries/action, then open and return from `View simulated original email`.

**Say:**

> I will open this course email. Here I can see the original sender, time, security result, category, priority, summary, and next action. The main point is clear before I read the full message.
>
> In the real product, “Open original in Gmail” opens the exact Gmail conversation. This demo opens a safe copy instead, so I can show the same experience without exposing private email.

### 2:58–3:20 — Action Items

**Actions:** Open Action Items. Point to one course deadline, the CloudNotes failed-payment item, and the completion control; do not change state.

**Say:**

> Next, I will open Action Items. This page only shows messages that need a real action. A deadline and a failed payment stay here, but a normal newsletter does not. I can complete an item without changing the original email, and processing it again will not create a duplicate.

### 3:20–3:52 — Topic knowledge base

**Actions:** Open Knowledge, pause on the topic list, open Project NOVA or AX4102, and show related messages in time order.

**Say:**

> Now I will open the knowledge base. Related emails are grouped into courses, projects, subscriptions, events, and support cases. I will open Project NOVA. Its messages appear together in time order, so I can understand the full story and later changes without searching for each email by hand.

### 3:52–4:15 — Cross-email QA and citations

**Actions:** Ask `What remains to be done for AX4102?` Point first to the answer and then to its source-email list.

**Say:**

> I can also ask a question across all emails. I will ask, “What remains to be done for AX4102?” The system finds relevant passages and creates one clear answer. The source emails appear below it, so I can open them and check the answer instead of simply trusting the model.

### 4:15–4:30 — Daily Digest

**Action:** Open Daily Digest and point to Urgent actions and Important updates.

**Say:**

> Finally, the daily digest separates urgent actions from important updates. Quarantined phishing content is excluded. I get a quick morning view, while every item still links back to its evidence.

---

## 4:30–5:00 — Evaluation and conclusion

### 4:30–4:52 — Actual evaluation results

**Action:** Return to presentation slide 4 or show the report chart. Point to each figure as it is spoken.

**Say:**

> I tested the project with twenty development emails, a separate holdout set, ten cross-email questions, and forty-two automated tests. DeepSeek reached 89.5 percent for intent, 73.7 percent for priority, and 79 percent for actions. Retrieval found the correct sources for all ten questions, but only six answers were fully acceptable. Answer quality is the main area to improve.

### 4:52–5:00 — Close

**Action:** End on the TraceInbox title or GitHub repository and face the camera.

**Say:**

> TraceInbox provides a privacy-safe and traceable email workflow. The code, synthetic data, evaluation, report, and setup guide are all in the GitHub repository. Thank you.

## Recording route

`Introduction → Welcome/setup → Import progress → Dashboard → Emails → Detail → Simulated original → Action Items → Knowledge → Cross-email QA → Daily Digest → Evaluation → Close`

## Practical reminders

- Let each page settle briefly after a click.
- Keep the pointer on the feature being discussed.
- Explain why a feature helps instead of reading every field.
- Wake Render before the official take.
- Use the prepared demo question and reproducible answer if model generation would be slow.
- If the take runs long, reduce scrolling and pauses; keep the evaluation and limitations.
