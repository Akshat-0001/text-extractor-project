import io
from unittest.mock import patch
from services import create_job


def test_list_jobs_empty(client):
    response = client.get("/jobs")
    assert response.status_code == 200
    assert response.json() == []


def test_list_jobs_returns_created_jobs(client, db):
    create_job(db, "file1.txt")
    create_job(db, "file2.txt")

    response = client.get("/jobs")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_jobs_filter_by_status(client, db):
    job = create_job(db, "done.txt")
    job.status = "completed"
    db.commit()
    create_job(db, "pending.txt")

    response = client.get("/jobs?status=completed")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "done.txt"


def test_list_jobs_search(client, db):
    create_job(db, "invoice_march.pdf")
    create_job(db, "report.txt")

    response = client.get("/jobs?search=invoice")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "invoice_march.pdf"


def test_get_job_detail(client, db):
    job = create_job(db, "detail.txt")

    response = client.get(f"/jobs/{job.id}")
    assert response.status_code == 200
    assert response.json()["filename"] == "detail.txt"


def test_get_job_detail_not_found(client):
    response = client.get("/jobs/9999")
    assert response.status_code == 404


def test_upload_creates_jobs(client):
    with patch("main.save_upload"), patch("main.process_document") as mock_task:
        mock_task.delay = lambda job_id: None

        files = [("files", ("test.txt", io.BytesIO(b"hello"), "text/plain"))]
        response = client.post("/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "test.txt"
    assert data[0]["status"] == "queued"


def test_update_result(client, db):
    job = create_job(db, "editable.txt")

    response = client.put(f"/jobs/{job.id}/result", json={
        "title": "Updated Title",
        "category": "Report",
        "keywords": ["one", "two"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["category"] == "Report"
    assert data["keywords"] == ["one", "two"]


def test_finalize_job(client, db):
    job = create_job(db, "final.txt")

    response = client.post(f"/jobs/{job.id}/finalize")
    assert response.status_code == 200
    assert response.json()["finalized"] == 1


def test_retry_job(client, db):
    job = create_job(db, "retry.txt")
    job.status = "failed"
    job.error_message = "timed out"
    db.commit()

    with patch("main.process_document") as mock_task:
        mock_task.delay = lambda job_id: None
        response = client.post(f"/jobs/{job.id}/retry")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["error_message"] is None


def test_export_json(client, db):
    from datetime import datetime
    job = create_job(db, "export.txt")
    job.status = "completed"
    job.title = "Export"
    job.category = "Document"
    job.summary = "Test"
    job.keywords = ["a", "b"]
    job.finalized = 1
    job.created_at = datetime(2024, 1, 1)
    job.updated_at = datetime(2024, 1, 1)
    db.commit()

    response = client.get(f"/jobs/{job.id}/export?format=json")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "export.txt"
    assert data["keywords"] == ["a", "b"]


def test_export_csv(client, db):
    from datetime import datetime
    job = create_job(db, "export.txt")
    job.status = "completed"
    job.title = "Export"
    job.category = "Document"
    job.summary = "Test"
    job.keywords = ["a", "b"]
    job.finalized = 1
    job.created_at = datetime(2024, 1, 1)
    job.updated_at = datetime(2024, 1, 1)
    db.commit()

    response = client.get(f"/jobs/{job.id}/export?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "export.txt" in response.text
