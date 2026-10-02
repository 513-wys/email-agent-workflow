# TraceInbox 五分钟演示录制脚本

## 录制前准备

- 画面比例使用 16:9、1080p。按照老师要求，整个视频都要让脸和电脑画面同时可见。
- 正式录制时打开 `/presenter`。页面上半部分是不会共享的提词板，下半部分是需要共享的动态介绍和产品演示。
- 在录屏软件中，只框选页面标记线下方的区域。提词板会根据下方页面自动切换提示。
- 点击提词板右上角的 `Start timer` 开始五分钟计时；`A−` 和 `A+` 可以调整英文讲稿字号。
- 提前唤醒 Render，确认每个页面都可以正常打开后再开始录制。
- 浏览器缩放保持在 90–100%。关闭通知、私人标签页以及任何真实邮箱、API Key、`.env` 或数据库画面。
- 动态介绍页使用键盘左右方向键切换。
- 英文正文约 620–650 词。保持自然语速，不需要刻意说快。

---

## 0:00–1:25｜项目介绍

### 0:00–0:22｜第一页：用真实场景开场

**操作提示（中文）：**

打开 `/presenter`，确认上方显示第一段提词、下方停留在动态标题页。前两个问题看着镜头说；说到 “TraceInbox is my answer” 时，再把视线和鼠标转向下方标题。

**英文口播：**

> Imagine opening your inbox and seeing a deadline, a project update, a payment problem, and a security alert together. Which one needs attention first? Which email has the latest information? TraceInbox is my answer. It turns scattered emails into clear actions, connected topics, and answers with sources.

### 0:22–0:43｜第二页：从场景自然带出问题

**操作提示（中文）：**

说完第一页的 “answers with sources” 后，按一次右方向键。等第二页完全出现，再说第一句。说到 “several messages” 时，用鼠标指向右侧第一张卡片。

**英文口播：**

> That is why I built TraceInbox. Email is easy to receive, but hard to organize. One task may be spread across several messages. A later email may change a deadline, and forwarding may hide the real sender. Search finds messages, but not the full story.

### 0:43–1:06｜第三页：从问题转向解决方法

**操作提示（中文）：**

说完 “not the full story” 后按右方向键。第三页出现后，用第一句话承接前面的问题。随后跟着 Import、Triage、Organize 和 Answer 的高亮顺序介绍。

**英文口播：**

> So how does it turn that messy inbox into something useful? TraceInbox imports new emails, checks security, and finds the original sender. It then creates actions and groups related messages into topics. Finally, it searches the local knowledge base and answers questions with links to the source emails.

### 1:06–1:18｜第四页：单独解释优势和评测

**操作提示（中文）：**

按右方向键进入第四页，并停留大约 12 秒。先指向 “Evidence before confidence”，再指向下方评测数字。这里不是只停两秒，而是完整讲完下面这段话。

**英文口播：**

> Before the live demo, this page shows the main advantage: traceability. Every action and answer links back to an original email. The evaluation also shows the system's limits.

### 1:18–1:25｜第五页：过渡到真实产品

**操作提示（中文）：**

讲完第四页的 “system's limits” 后，再按一次右方向键。第五页出现后，说下面这句；说完再点击 “Open TraceInbox demo”。这样第五页承担的是正式转场作用。

**英文口播：**

> With that idea in mind, let us move from the overview to the live product.

---

## 1:25–4:30｜边操作边讲解产品

### 1:25–2:00｜首页：连接邮箱和首次导入

**操作提示（中文）：**

1. 进入公开演示首页后，先把鼠标放在 “Connected mailbox” 输入框上。
2. 再指向其他邮箱地址区域。
3. 指向 API Key 和首次导入数量。
4. 点击进入演示或开始导入的按钮。

**英文口播：**

> This is the first page a new user sees. Here, I enter the main mailbox I want to connect. I can also add other addresses that belong to me. For example, I may forward my university email into Gmail. TraceInbox reads the forwarding information and shows the original sender, not my own address.
>
> I can choose DeepSeek or a local Ollama model, and choose how many recent emails to import. The default is one hundred. In this demo, all values are fictional and nothing is saved or sent outside the app. I will now start the import.

### 2:00–2:25｜导入进度和 Dashboard

**操作提示（中文）：**

1. 让导入进度页短暂显示。
2. 完成后进入 Dashboard。
3. 鼠标依次指向 Emails processed、High priority、Quarantined 和 Next actions。

**英文口播：**

> During the first import, I can see the progress instead of waiting on a blank page. This demo loads twenty connected emails. The dashboard then shows the processed emails, urgent items, quarantined messages, and my next actions. I can understand the situation before opening every message.

### 2:25–2:58｜邮件详情和原邮件跳转

**操作提示（中文）：**

1. 点击 Emails。
2. 打开一封有代表性的课程邮件，例如 AX4102。
3. 指向真实发件人、分类、优先级、中文/英文摘要和行动事项。
4. 点击 “View simulated original email”，展示模拟 Gmail 原邮件，然后返回。

**英文口播：**

> I will open this course email. Here I can see the original sender, time, security result, category, priority, summary, and next action. The main point is clear before I read the full message.
>
> In the real product, “Open original in Gmail” opens the exact Gmail conversation. This demo opens a safe copy instead, so I can show the same experience without exposing private email.

### 2:58–3:20｜行动事项

**操作提示（中文）：**

1. 点击顶部导航栏的 Action Items。
2. 指向一个课程截止日期和 CloudNotes 付款失败事项。
3. 不必真的修改状态；只指出完成按钮即可。

**英文口播：**

> Next, I will open Action Items. This page only shows messages that need a real action. A deadline and a failed payment stay here, but a normal newsletter does not. I can complete an item without changing the original email, and processing it again will not create a duplicate.

### 3:20–3:52｜主题知识库

**操作提示（中文）：**

1. 点击 Knowledge。
2. 先停留在主题列表，让观众看到不同主题。
3. 打开 Project NOVA 或 AX4102。
4. 向下滚动，展示同一主题下按时间排列的多封邮件。

**英文口播：**

> Now I will open the knowledge base. Related emails are grouped into courses, projects, subscriptions, events, and support cases. I will open Project NOVA. Its messages appear together in time order, so I can understand the full story and later changes without searching for each email by hand.

### 3:52–4:15｜跨邮件问答和来源引用

**操作提示（中文）：**

1. 进入问答区域。
2. 输入或选择示例问题：`What remains to be done for AX4102?`
3. 点击 Ask。
4. 回答出现后，先指答案，再指下方来源邮件列表。

**英文口播：**

> I can also ask a question across all emails. I will ask, “What remains to be done for AX4102?” The system finds relevant passages and creates one clear answer. The source emails appear below it, so I can open them and check the answer instead of simply trusting the model.

### 4:15–4:30｜每日晨报

**操作提示（中文）：**

点击 Daily Digest，指向 Urgent actions 和 Important updates 两个区域。

**英文口播：**

> Finally, the daily digest separates urgent actions from important updates. Quarantined phishing content is excluded. I get a quick morning view, while every item still links back to its evidence.

---

## 4:30–5:00｜评测和总结

### 4:30–4:52｜展示真实评测结果

**操作提示（中文）：**

切回动态介绍页的第四页，或者展示 Word 报告里的评测图表。说到每一个数字时，用鼠标指向对应数据。

**英文口播：**

> I tested the project with twenty development emails, a separate holdout set, ten cross-email questions, and forty-two automated tests. DeepSeek reached 89.5 percent for intent, 73.7 percent for priority, and 79 percent for actions. Retrieval found the correct sources for all ten questions, but only six answers were fully acceptable. Answer quality is the main area to improve.

### 4:52–5:00｜结束

**操作提示（中文）：**

停在 TraceInbox 标题页或 GitHub 仓库首页，看向镜头完成最后一句。

**英文口播：**

> TraceInbox provides a privacy-safe and traceable email workflow. The code, synthetic data, evaluation, report, and setup guide are all in the GitHub repository. Thank you.

---

## 最终录制路线

`动态介绍 → 首页设置 → 导入进度 → Dashboard → Emails → 邮件详情 → Simulated original → Action Items → Knowledge → Cross-email Q&A → Daily Digest → 评测结果 → 结束`

## 录制时的实用提醒

- 每次点击后先等页面稳定半秒，再继续讲话。
- 鼠标只在你正在介绍的位置停留，不要无目的地快速移动。
- 不要逐字段读页面；重点说明“用户为什么需要它”和“这个动作解决了什么问题”。
- 如果 Render 需要唤醒，请在正式录制前完成，不要把加载过程录进去。
- 如果问答生成较慢，使用已经准备好的示例问题和演示答案。
- 如果超过五分钟，先减少滚动和鼠标停顿，不要删掉评测结果和项目局限。
