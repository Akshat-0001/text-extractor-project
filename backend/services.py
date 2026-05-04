import os
import json
from sqlalchemy.orm import Session
from models import Job

def save_upload(filename: str, content: bytes) -> str:
    os.makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath

def create_job(db: Session, filename: str) -> Job:
    job = Job(filename=filename, status="queued", progress="document_received")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: int) -> Job:
    return db.query(Job).filter(Job.id == job_id).first()

def get_jobs(db: Session, search: str = None, status: str = None, sort: str = "desc"):
    query = db.query(Job)
    
    if search:
        query = query.filter(Job.filename.ilike(f"%{search}%"))
    
    if status:
        query = query.filter(Job.status == status)
    
    if sort == "asc":
        query = query.order_by(Job.created_at.asc())
    else:
        query = query.order_by(Job.created_at.desc())
    
    return query.all()

def update_job_progress(db: Session, job_id: int, status: str, progress: str):
    job = get_job(db, job_id)
    if job:
        job.status = status
        job.progress = progress
        db.commit()

def update_job_result(db: Session, job_id: int, title: str, category: str, summary: str, keywords: list):
    job = get_job(db, job_id)
    if job:
        job.title = title
        job.category = category
        job.summary = summary
        job.keywords = keywords
        job.result = {
            "title": title,
            "category": category,
            "summary": summary,
            "keywords": keywords
        }
        db.commit()

def update_job_fields(db: Session, job_id: int, data: dict):
    job = get_job(db, job_id)
    if job:
        if "title" in data:
            job.title = data["title"]
        if "category" in data:
            job.category = data["category"]
        if "summary" in data:
            job.summary = data["summary"]
        if "keywords" in data:
            job.keywords = data["keywords"]
        db.commit()
        db.refresh(job)
    return job

def finalize_job(db: Session, job_id: int):
    job = get_job(db, job_id)
    if job:
        job.finalized = 1
        db.commit()

def mark_job_failed(db: Session, job_id: int, error: str):
    job = get_job(db, job_id)
    if job:
        job.status = "failed"
        job.error_message = error
        db.commit()

def export_job_json(job: Job) -> dict:
    return {
        "id": job.id,
        "filename": job.filename,
        "status": job.status,
        "title": job.title,
        "category": job.category,
        "summary": job.summary,
        "keywords": job.keywords,
        "finalized": bool(job.finalized),
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat()
    }

def export_job_csv(job: Job) -> str:
    keywords_str = ",".join(job.keywords) if job.keywords else ""
    return f"{job.id},{job.filename},{job.status},{job.title},{job.category},{job.summary},{keywords_str},{job.finalized}"
