import os
import time
import json
from fastapi import FastAPI, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import redis

from database import get_db, init_db
from models import Job
from schemas import JobResponse, JobUpdate
from services import (
    save_upload, create_job, get_job, get_jobs,
    update_job_fields, finalize_job, export_job_json, export_job_csv
)
from worker import process_document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

@app.on_event("startup")
def startup():
    # Postgres may still be initializing when this container starts, retry a few times
    for attempt in range(10):
        try:
            init_db()
            return
        except Exception:
            if attempt == 9:
                raise
            time.sleep(2)

@app.post("/upload", response_model=List[JobResponse])
async def upload_documents(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    jobs = []
    for file in files:
        content = await file.read()
        save_upload(file.filename, content)
        job = create_job(db, file.filename)
        process_document.delay(job.id)
        jobs.append(job)
    return jobs

@app.get("/jobs", response_model=List[JobResponse])
def list_jobs(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort: str = Query("desc"),
    db: Session = Depends(get_db)
):
    return get_jobs(db, search, status, sort)

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    return job

@app.get("/jobs/{job_id}/progress")
async def job_progress(job_id: int):
    def event_stream():
        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"job:{job_id}")
        
        for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"].decode("utf-8")
                yield f"data: {data}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/jobs/{job_id}/retry", response_model=JobResponse)
def retry_job(job_id: int, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    
    job.status = "queued"
    job.progress = "document_received"
    job.error_message = None
    db.commit()
    db.refresh(job)
    
    process_document.delay(job.id)
    return job

@app.put("/jobs/{job_id}/result", response_model=JobResponse)
def update_result(job_id: int, data: JobUpdate, db: Session = Depends(get_db)):
    job = update_job_fields(db, job_id, data.model_dump(exclude_unset=True))
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    return job

@app.post("/jobs/{job_id}/finalize", response_model=JobResponse)
def finalize_job_endpoint(job_id: int, db: Session = Depends(get_db)):
    finalize_job(db, job_id)
    job = get_job(db, job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    return job

@app.get("/jobs/{job_id}/export")
def export_job(job_id: int, format: str = Query("json"), db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    
    if format == "csv":
        csv_header = "id,filename,status,title,category,summary,keywords,finalized\n"
        csv_data = csv_header + export_job_csv(job)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=job_{job_id}.csv"}
        )
    else:
        return export_job_json(job)
