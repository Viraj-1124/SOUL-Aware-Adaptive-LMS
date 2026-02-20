from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Attendance


def mark_attendance(db: Session, data):
    attendance = Attendance(**data.dict())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def get_student_attendance(db: Session, student_id: int):
    return db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()


def calculate_attendance_rate(db: Session, student_id: int, course_id: int):
    total_classes = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id
    ).scalar()

    present_classes = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id,
        Attendance.present == True
    ).scalar()

    if total_classes == 0:
        return 0

    return round((present_classes / total_classes) * 100, 2)
