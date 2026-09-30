"""In-process background jobs for the one-time mailbox import."""
from copy import deepcopy
from datetime import datetime
from threading import Lock, Thread
from uuid import uuid4

from app import pipeline, settings_store


_jobs = {}
_lock = Lock()


def _update(job_id, **values):
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(values)


def get(job_id):
    with _lock:
        job = _jobs.get(job_id)
        return deepcopy(job) if job else None


def _run(job_id, limit):
    try:
        def progress(event):
            _update(job_id, **event)

        result = pipeline.ingest(limit=limit, progress_callback=progress)
        settings_store.set("initial_sync_completed", "1")
        _update(
            job_id,
            status="complete",
            phase="complete",
            processed=result["inserted"] + result["failed"] + result["skipped"],
            inserted=result["inserted"],
            skipped=result["skipped"],
            failed=result["failed"],
            older_skipped=result.get("older_skipped", 0),
            finished_at=datetime.now().astimezone().isoformat(),
        )
    except Exception as exc:
        _update(job_id, status="failed", phase="failed", error=str(exc)[:240])


def start(limit):
    job_id = uuid4().hex
    with _lock:
        _jobs[job_id] = {
            "id": job_id, "status": "running", "phase": "connecting",
            "total": 0, "processed": 0, "inserted": 0, "skipped": 0,
            "failed": 0, "older_skipped": 0, "error": "",
            "started_at": datetime.now().astimezone().isoformat(),
        }
    Thread(target=_run, args=(job_id, limit), daemon=True).start()
    return job_id
