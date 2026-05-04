from datetime import datetime
from services import (
    create_job, get_job, get_jobs,
    update_job_fields, finalize_job, mark_job_failed,
    export_job_json, export_job_csv
)
from models import Job


def test_create_job(db):
    job = create_job(db, "report.pdf")
    assert job.id is not None
    assert job.filename == "report.pdf"
    assert job.status == "queued"
    assert job.progress == "document_received"
    assert job.finalized == 0


def test_get_job_returns_none_for_missing(db):
    assert get_job(db, 9999) is None


def test_get_jobs_filters_by_status(db):
    create_job(db, "a.txt")
    job = create_job(db, "b.txt")
    job.status = "completed"
    db.commit()

    results = get_jobs(db, status="completed")
    assert len(results) == 1
    assert results[0].filename == "b.txt"


def test_get_jobs_search_by_filename(db):
    create_job(db, "invoice_2024.pdf")
    create_job(db, "report.txt")

    results = get_jobs(db, search="invoice")
    assert len(results) == 1
    assert results[0].filename == "invoice_2024.pdf"


def test_update_job_fields_partial(db):
    job = create_job(db, "doc.txt")
    updated = update_job_fields(db, job.id, {"title": "My Doc"})
    assert updated.title == "My Doc"
    assert updated.category is None  # untouched


def test_update_job_fields_ignores_missing_job(db):
    result = update_job_fields(db, 9999, {"title": "Ghost"})
    assert result is None


def test_finalize_job(db):
    job = create_job(db, "final.txt")
    finalize_job(db, job.id)
    db.refresh(job)
    assert job.finalized == 1


def test_mark_job_failed(db):
    job = create_job(db, "broken.txt")
    mark_job_failed(db, job.id, "something went wrong")
    db.refresh(job)
    assert job.status == "failed"
    assert job.error_message == "something went wrong"


def test_export_job_json(db):
    job = create_job(db, "export_me.txt")
    job.status = "completed"
    job.title = "Export Me"
    job.category = "Document"
    job.summary = "A test doc"
    job.keywords = ["test", "export"]
    job.finalized = 1
    job.created_at = datetime(2024, 1, 1, 12, 0, 0)
    job.updated_at = datetime(2024, 1, 1, 12, 0, 0)
    db.commit()

    result = export_job_json(job)
    assert result["filename"] == "export_me.txt"
    assert result["title"] == "Export Me"
    assert result["keywords"] == ["test", "export"]
    assert result["finalized"] is True


def test_export_job_csv(db):
    job = create_job(db, "data.txt")
    job.title = "Data"
    job.category = "Document"
    job.summary = "Summary"
    job.keywords = ["data", "test"]
    db.commit()

    csv_row = export_job_csv(job)
    assert "data.txt" in csv_row
    assert "Data" in csv_row
    assert "data,test" in csv_row
