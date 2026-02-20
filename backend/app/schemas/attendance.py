from pydantic import BaseModel
from datetime import date

class AttendanceCreate(BaseModel):
    student_id: int
    course_id: int
    date: date
    present: bool


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    date: date
    present: bool

    class Config:
        from_attributes = True
