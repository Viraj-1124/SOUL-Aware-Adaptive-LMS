from sqlalchemy.orm import Session
from app.models.activity import StudentActivityLog
from datetime import datetime

ALLOWED_ACTIVITIES = {
    "login",
    "logout",
    "course_open",
    "video_watch",
    "assignment_open",
    "assignment_submit",
    "quiz_start",
    "quiz_submit",
    "page_view",
    "idle_time",
}

def log_activity(db: Session, student_id: int, data):

    is_valid = data.activity_type in ALLOWED_ACTIVITIES or data.activity_type.startswith("page_view")
    if not is_valid:
        raise ValueError("Invalid activity type")

    log = StudentActivityLog(
        student_id=student_id,
        course_id=data.course_id,
        activity_type=data.activity_type,
        duration_seconds=data.duration_seconds,
        metadata=data.metadata
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log