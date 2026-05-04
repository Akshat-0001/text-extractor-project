import json
from unittest.mock import MagicMock, patch, call
from worker import process_document, STAGES


def make_db_with_job(filename="test_document.txt"):
    job = MagicMock()
    job.id = 1
    job.filename = filename

    db = MagicMock()
    return db, job


def test_stages_list_has_six_entries():
    assert len(STAGES) == 6


def test_last_stage_is_completed():
    last_status, last_progress, _ = STAGES[-1]
    assert last_status == "completed"
    assert last_progress == "job_completed"


def test_process_document_publishes_one_event_per_stage():
    db = MagicMock()
    job = MagicMock()
    job.id = 1
    job.filename = "my_report.txt"

    with patch("worker.SessionLocal", return_value=db), \
         patch("worker.get_job", return_value=job), \
         patch("worker.update_job_progress"), \
         patch("worker.update_job_result"), \
         patch("worker.redis_client") as mock_redis, \
         patch("worker.time.sleep"):

        process_document(1)

    assert mock_redis.publish.call_count == len(STAGES)


def test_process_document_publishes_to_correct_channel():
    db = MagicMock()
    job = MagicMock()
    job.id = 42
    job.filename = "file.txt"

    with patch("worker.SessionLocal", return_value=db), \
         patch("worker.get_job", return_value=job), \
         patch("worker.update_job_progress"), \
         patch("worker.update_job_result"), \
         patch("worker.redis_client") as mock_redis, \
         patch("worker.time.sleep"):

        process_document(42)

    for publish_call in mock_redis.publish.call_args_list:
        channel = publish_call[0][0]
        assert channel == "job:42"


def test_process_document_extracts_title_from_filename():
    db = MagicMock()
    job = MagicMock()
    job.id = 1
    job.filename = "annual_report_2024.pdf"

    with patch("worker.SessionLocal", return_value=db), \
         patch("worker.get_job", return_value=job), \
         patch("worker.update_job_progress"), \
         patch("worker.update_job_result") as mock_result, \
         patch("worker.redis_client"), \
         patch("worker.time.sleep"):

        process_document(1)

    args = mock_result.call_args[0]
    title = args[2]
    assert title == "Annual Report 2024"


def test_process_document_marks_failed_on_exception():
    db = MagicMock()

    with patch("worker.SessionLocal", return_value=db), \
         patch("worker.get_job", side_effect=Exception("db exploded")), \
         patch("worker.mark_job_failed") as mock_fail, \
         patch("worker.redis_client") as mock_redis, \
         patch("worker.time.sleep"):

        process_document(1)

    mock_fail.assert_called_once()
    error_msg = mock_fail.call_args[0][2]
    assert "db exploded" in error_msg


def test_process_document_publishes_failure_event_on_exception():
    db = MagicMock()

    with patch("worker.SessionLocal", return_value=db), \
         patch("worker.get_job", side_effect=Exception("boom")), \
         patch("worker.mark_job_failed"), \
         patch("worker.redis_client") as mock_redis, \
         patch("worker.time.sleep"):

        process_document(5)

    mock_redis.publish.assert_called_once()
    channel, payload = mock_redis.publish.call_args[0]
    event = json.loads(payload)
    assert event["status"] == "failed"
    assert event["progress"] == "job_failed"


def test_process_document_does_nothing_if_job_not_found():
    db = MagicMock()

    with patch("worker.SessionLocal", return_value=db), \
         patch("worker.get_job", return_value=None), \
         patch("worker.update_job_progress") as mock_progress, \
         patch("worker.redis_client") as mock_redis:

        process_document(999)

    mock_progress.assert_not_called()
    mock_redis.publish.assert_not_called()
