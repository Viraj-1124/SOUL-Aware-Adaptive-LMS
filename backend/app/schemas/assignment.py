from pydantic import BaseModel
from datetime import datetime

class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    description: str
    due_date: datetime


class AssignmentResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: str
    due_date: datetime

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    assignment_id: int
    submission_text: str
    reflection_text: str


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    score: float | None
    sentiment_score: float | None
    reflection_depth: float | None

    class Config:
        from_attributes = True
