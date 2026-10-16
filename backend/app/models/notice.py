from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NoticeCreate(BaseModel):
    """Payload to publish a new institutional announcement."""
    title: str = Field(..., min_length=3, max_length=200)
    category: str = Field(..., pattern=r"^(academic|examination|administrative|fees|event|urgent)$", description="academic, examination, administrative, fees, event, urgent")
    content: str = Field(..., min_length=5)
    target_role: str = Field("all", description="all, student, faculty")
    is_published: bool = True


class NoticeItem(BaseModel):
    """Institutional notice item for campus broadcast."""
    id: str
    title: str
    category: str
    content: str
    published_by_name: Optional[str] = None
    is_published: bool = True
    target_role: str = "all"
    published_at: datetime
