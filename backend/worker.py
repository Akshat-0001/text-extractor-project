import os
import time
import json
from celery import Celery
from database import SessionLocal
from services import update_job_progress, update_job_result, mark_job_failed, get_job
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.broker_connection_retry_on_startup = True
redis_client = redis.from_url(REDIS_URL)

STAGES = [
    ("processing", "parsing_started", "Parsing document"),
    ("processing", "parsing_completed", "Parsing completed"),
    ("processing", "extraction_started", "Extracting fields"),
    ("processing", "extraction_completed", "Extraction completed"),
    ("processing", "storing_result", "Storing result"),
    ("completed", "job_completed", "Processing completed")
]

@celery_app.task
def process_document(job_id: int):
    db = SessionLocal()
    
    try:
        job = get_job(db, job_id)
        if not job:
            return
        
        for status, progress, message in STAGES:
            update_job_progress(db, job_id, status, progress)
            
            event = {
                "job_id": job_id,
                "status": status,
                "progress": progress,
                "message": message
            }
            redis_client.publish(f"job:{job_id}", json.dumps(event))
            
            time.sleep(1)
        
        filename = job.filename
        title = filename.rsplit(".", 1)[0].replace("_", " ").title()
        category = "Document"
        summary = f"Processed document: {filename}"
        keywords = [word for word in filename.lower().replace("_", " ").split() if len(word) > 3]
        
        update_job_result(db, job_id, title, category, summary, keywords)
        
    except Exception as e:
        mark_job_failed(db, job_id, str(e))
        event = {
            "job_id": job_id,
            "status": "failed",
            "progress": "job_failed",
            "message": f"Error: {str(e)}"
        }
        redis_client.publish(f"job:{job_id}", json.dumps(event))
    
    finally:
        db.close()
