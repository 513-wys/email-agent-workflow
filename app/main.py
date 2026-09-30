"""Flask 应用：中文 Web 界面 + 路由。"""
import json
import re

from flask import Flask, jsonify, make_response, redirect, render_template, request, url_for
from urllib.parse import urlsplit

from app import config, db, demo_seed, digest as digest_mod, import_jobs, notify, pipeline, rag, settings_store, topics
from app.i18n import LANGUAGES, category_label, priority_label, status_label, translate
from app.mail_links import gmail_message_url

app = Flask(__name__)
db.init_db()
settings_store.init_table()
if config.PUBLIC_DEMO:
    demo_seed.seed()
    settings_store.set("initial_sync_completed", "1")


def _language():
    return request.cookies.get("language") if request.cookies.get("language") in LANGUAGES else "en"


@app.context_processor
def inject_i18n():
    lang = _language()
    return {
        "lang": lang,
        "t": lambda key, **values: translate(lang, key, **values),
        "status_label": lambda value: status_label(lang, value),
        "category_label": lambda email: category_label(lang, email.get("intent"), email.get("category")),
        "priority_label": lambda value: priority_label(lang, value),
        "public_demo": config.PUBLIC_DEMO,
    }


@app.route("/language/<lang>")
def set_language(lang):
    if lang not in LANGUAGES:
        lang = "en"
    target = request.args.get("next", "/")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/"):
        target = "/"
    response = make_response(redirect(target))
    response.set_cookie("language", lang, max_age=31536000, samesite="Lax")
    return response


@app.route("/")
def home():
    if config.PUBLIC_DEMO:
        return redirect(url_for("dashboard"))
    if settings_store.get("initial_sync_completed", "0") != "1":
        return redirect(url_for("onboarding"))
    return render_template("onboarding.html", ready=True, s=settings_store.get_all_masked())


@app.route("/dashboard")
def dashboard():
    if settings_store.get("initial_sync_completed", "0") != "1":
        return redirect(url_for("onboarding"))
    st = db.stats()
    recent = db.list_emails(limit=15)
    return render_template(
        "dashboard.html", stats=st, emails=recent,
        recent_actions=db.list_action_items("OPEN", limit=5),
        action_counts=db.action_stats(),
        knowledge_stats=db.knowledge_stats(),
    )


@app.route("/enter", methods=["POST"])
def enter_workspace():
    if settings_store.get("initial_sync_completed", "0") != "1":
        return redirect(url_for("onboarding"))
    owner_emails = request.form.get("owner_emails", "")
    mail_user = settings_store.get("mail_user", config.IMAP_USER) or ""
    owners = sorted(set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", owner_emails, re.I) + [mail_user]))
    normalized = "\n".join(address.lower() for address in owners if address)
    settings_store.set("owner_emails", normalized)
    db.normalize_existing_forwarded(normalized)
    return redirect(url_for("dashboard"))


@app.route("/ingest", methods=["POST"])
def ingest():
    if config.PUBLIC_DEMO:
        return redirect(url_for("dashboard", demo="readonly"))
    if settings_store.get("initial_sync_completed", "0") != "1":
        return redirect(url_for("onboarding"))
    batch = pipeline.ingest(limit=500)
    for r in batch["results"]:
        if r.get("status") == "已隔离":
            notify.send(
                f"🚨【安全告警】拦截高危邮件\n"
                f"👤 发件人: {r.get('sender')}\n"
                f"📝 主题: {r.get('subject')}\n"
                f"⚠️ 威胁评分: {r.get('threat_score')}/100（{r.get('risk_level')}）"
            )
    return redirect(url_for(
        "dashboard", inserted=batch["inserted"], skipped=batch["skipped"],
        failed=batch["failed"], remaining=batch.get("remaining", 0),
        older_skipped=batch.get("older_skipped", 0)
    ))


@app.route("/onboarding")
def onboarding():
    if config.PUBLIC_DEMO:
        return redirect(url_for("dashboard"))
    if settings_store.get("initial_sync_completed", "0") == "1":
        return redirect(url_for("dashboard"))
    job_id = request.args.get("job", "")
    job = import_jobs.get(job_id) if job_id else None
    return render_template(
        "onboarding.html", s=settings_store.get_all_masked(),
        providers=settings_store.PROVIDERS, job=job, job_id=job_id, ready=False,
        error=request.args.get("error", ""),
    )


@app.route("/onboarding/start", methods=["POST"])
def onboarding_start():
    if config.PUBLIC_DEMO:
        return redirect(url_for("dashboard"))
    provider = request.form.get("mail_provider", "gmail")
    mail_user = request.form.get("mail_user", "").strip()
    mail_password = request.form.get("mail_password", "").strip()
    owner_emails = request.form.get("owner_emails", "").strip()
    if provider not in settings_store.PROVIDERS:
        provider = "gmail"
    if not mail_user or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", mail_user):
        return redirect(url_for("onboarding", error="email"))
    if not mail_password and not settings_store.get("mail_password", config.IMAP_PASSWORD):
        return redirect(url_for("onboarding", error="password"))
    try:
        limit = max(1, min(int(request.form.get("initial_sync_limit", "100")), 500))
    except (TypeError, ValueError):
        limit = 100

    settings_store.set("mail_mode", "real")
    settings_store.set("mail_provider", provider)
    settings_store.set("mail_user", mail_user)
    owners = sorted(set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", owner_emails, re.I) + [mail_user]))
    settings_store.set("owner_emails", "\n".join(address.lower() for address in owners))
    if mail_password:
        settings_store.set("mail_password", mail_password)
    settings_store.set("initial_sync_limit", str(limit))
    settings_store.set("initial_sync_completed", "0")
    job_id = import_jobs.start(limit)
    return redirect(url_for("onboarding", job=job_id))


@app.route("/onboarding/status/<job_id>")
def onboarding_status(job_id):
    job = import_jobs.get(job_id)
    if not job:
        return jsonify({"status": "missing"}), 404
    return jsonify(job)


@app.route("/emails")
def emails():
    status = request.args.get("status", "")
    intent = request.args.get("intent", "")
    rows = db.list_emails(status=status or None, intent=intent or None)
    return render_template("emails.html", emails=rows, status=status, intent=intent)


@app.route("/actions")
def action_items_page():
    status = request.args.get("status", "OPEN").upper()
    if status not in {"OPEN", "DONE", "DISMISSED", "EXPIRED", "ALL"}:
        status = "OPEN"
    rows = db.list_action_items(None if status == "ALL" else status)
    return render_template(
        "action_items.html", actions=rows, selected_status=status,
        action_counts=db.action_stats(),
    )


@app.route("/actions/<int:action_id>/status", methods=["POST"])
def action_item_status(action_id):
    if config.PUBLIC_DEMO:
        return redirect(url_for("action_items_page"))
    status = request.form.get("status", "").upper()
    db.set_action_status(action_id, status)
    selected = request.form.get("selected_status", "OPEN")
    return redirect(url_for("action_items_page", status=selected))


@app.route("/knowledge")
def knowledge_page():
    topics.rebuild()
    return render_template("knowledge.html", topics=db.list_topics(), result=None, question="")


@app.route("/knowledge/ask", methods=["POST"])
def knowledge_ask():
    question = request.form.get("question", "").strip()[:1000]
    topic_id = request.form.get("topic_id", type=int)
    error = ""
    try:
        result = rag.answer(question, topic_id=topic_id) if question else None
    except Exception:
        result = None
        error = translate(_language(), "answer_failed")
    selected_topic = db.get_topic(topic_id)[0] if topic_id else None
    return render_template(
        "knowledge.html", topics=db.list_topics(), result=result, question=question,
        selected_topic=selected_topic, error=error,
    )


@app.route("/knowledge/topics/<int:topic_id>")
def knowledge_topic(topic_id):
    topic, rows = db.get_topic(topic_id)
    if not topic:
        return redirect(url_for("knowledge_page"))
    return render_template("knowledge_topic.html", topic=topic, emails=rows)


@app.route("/emails/<int:email_id>")
def email_detail(email_id):
    e = db.get_email(email_id)
    if not e:
        return redirect(url_for("emails"))
    ctx = json.loads(e.get("context_json") or "{}")
    precise_link = ""
    if e.get("provider_thread_id") and (e.get("provider") or "").upper() == "GMAIL":
        precise_link = gmail_message_url(
            settings_store.get("mail_user", ""), e["provider_thread_id"]
        )
    elif e.get("original_url") or e.get("gmail_link"):
        precise_link = e.get("original_url") or e.get("gmail_link") or ""
    is_demo = (e.get("provider") == "DEMO") or str(e.get("message_id") or "").startswith("demo-")
    return render_template(
        "email_detail.html", e=e, ctx=ctx, analysis=db.get_email_analysis(email_id),
        original_link=precise_link, is_demo=is_demo
    )


@app.route("/digest")
def digest_page():
    return render_template("digest.html", digest=None)


@app.route("/digest", methods=["POST"])
def digest_generate():
    rows = db.list_emails(limit=100)
    todos = [
        r for r in rows
        if r.get("priority") in ("P0_CRITICAL", "P1_HIGH") and r.get("status") == "已分类"
    ]
    if config.PUBLIC_DEMO:
        high = [row for row in rows if row.get("priority") in ("P0_CRITICAL", "P1_HIGH")]
        text = "## Demo inbox brief\n\n" + "\n".join(
            f"- {row.get('subject')}: {row.get('summary')}" for row in high
        )
    else:
        text = digest_mod.generate(rows, todos)
    return render_template("digest.html", digest=text)


@app.route("/settings")
def settings_page():
    if config.PUBLIC_DEMO:
        return redirect(url_for("dashboard"))
    return render_template(
        "settings.html", s=settings_store.get_all_masked(), providers=settings_store.PROVIDERS, saved=False
    )


@app.route("/settings", methods=["POST"])
def settings_save():
    if config.PUBLIC_DEMO:
        return redirect(url_for("dashboard"))
    api_key = request.form.get("deepseek_api_key", "").strip()
    if api_key:
        settings_store.set("deepseek_api_key", api_key)

    mail_mode = request.form.get("mail_mode", "demo")
    previous_identity = (
        settings_store.get("mail_mode", "demo"),
        settings_store.get("mail_provider", "gmail"),
        (settings_store.get("mail_user", config.IMAP_USER) or "").strip().lower(),
    )
    settings_store.set("mail_mode", mail_mode)

    if mail_mode == "real":
        provider = request.form.get("mail_provider", "gmail")
        if provider in settings_store.PROVIDERS:
            settings_store.set("mail_provider", provider)

        mail_user = request.form.get("mail_user", "").strip()
        if mail_user:
            settings_store.set("mail_user", mail_user)

        mail_password = request.form.get("mail_password", "").strip()
        if mail_password:
            settings_store.set("mail_password", mail_password)

    try:
        initial_sync_limit = int(request.form.get("initial_sync_limit", "100"))
    except (TypeError, ValueError):
        initial_sync_limit = 100
    settings_store.set("initial_sync_limit", str(max(1, min(initial_sync_limit, 500))))

    current_identity = (
        settings_store.get("mail_mode", "demo"),
        settings_store.get("mail_provider", "gmail"),
        (settings_store.get("mail_user", config.IMAP_USER) or "").strip().lower(),
    )
    if current_identity != previous_identity:
        settings_store.set("initial_sync_completed", "0")

    return render_template(
        "settings.html", s=settings_store.get_all_masked(), providers=settings_store.PROVIDERS, saved=True
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "mode": "public-demo" if config.PUBLIC_DEMO else "personal"})
