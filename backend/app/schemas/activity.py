from pydantic import BaseModel
from typing import Optional, Dict

class ActivityCreate(BaseModel):
    course_id: Optional[int]
    activity_type: str
    duration_seconds: Optional[float] = 0
    metadata: Optional[Dict] = None