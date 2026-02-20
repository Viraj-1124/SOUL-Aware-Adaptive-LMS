from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AttendanceCreate, AttendanceResponse
from app.services.attendance_service import (
    mark_attendance,
    get_student_attendance,
    calculate_attendance_rate
)
from app.auth.dependencies import require_role
router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/mark", response_model=AttendanceResponse)
def mark(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "instructor"]))
):
    return mark_attendance(db, data)

@router.get("/student/{student_id}")
def student_attendance(
    student_id: int,
    db: Session = Depends(get_db)
):
    return get_student_attendance(db, student_id)


@router.get("/rate/{student_id}/{course_id}")
def attendance_rate(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db)
):
    rate = calculate_attendance_rate(db, student_id, course_id)
    return {"attendance_rate": rate}
