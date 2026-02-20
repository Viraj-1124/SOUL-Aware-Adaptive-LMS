from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import AssignmentSubmission


def calculate_academic_mastery(db: Session, student_id: int):
    avg_score = db.query(func.avg(AssignmentSubmission.score)).filter(
        AssignmentSubmission.student_id == student_id
    ).scalar()

    return round(avg_score or 0, 2)