"""Pydantic models for Search Information Module."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SearchItem(BaseModel):
    """Institutional academic information item filterable by branch, year, category, and subject."""
    id: str
    branch: str
    year: int = Field(..., ge=1, le=4, description="Academic year (1-4)")
    category: str = Field(..., description="Information category (Syllabus, Timetable, Results, Fees, FAQ)")
    subject: str = Field(..., description="Course subject name or department")
    title: str = Field(..., description="Document or notice title")
    content_details: str = Field(..., description="Full text summary or syllabus/rule content")
    file_url: Optional[str] = Field(None, description="Document URL or reference path")
    created_at: Optional[datetime] = None
