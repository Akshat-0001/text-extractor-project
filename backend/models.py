from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="queued")
    progress = Column(String, default="document_received")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    
    title = Column(String, nullable=True)
    category = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    finalized = Column(Integer, default=0)
