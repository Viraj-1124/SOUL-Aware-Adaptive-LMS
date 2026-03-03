from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.ai_engine.fatigue_detector import detect_moral_fatigue

router = APIRouter(prefix="/fatigue", tags=["Moral Fatigue"])

@router.post("/{student_id}/{course_id}")
def check_fatigue(student_id: int, course_id: int, db: Session = Depends(get_db)):
    return detect_moral_fatigue(db, student_id, course_id)