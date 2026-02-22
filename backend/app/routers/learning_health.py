from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.learning_health_service import compute_learning_health
from app.auth.dependencies import require_role

router = APIRouter(prefix="/learning-health", tags=["Learning Health"])

@router.post("/{student_id}/{course_id}")
def generate_health(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "INSTRUCTOR"]))
):
    return compute_learning_health(db, student_id, course_id)