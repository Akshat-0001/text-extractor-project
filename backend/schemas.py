from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class JobResponse(BaseModel):
    id: int
    filename: str
    status: str
    progress: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    finalized: int

    class Config:
        from_attributes = True

class JobUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None

class ProgressEvent(BaseModel):
    job_id: int
    status: str
    progress: str
    message: str
