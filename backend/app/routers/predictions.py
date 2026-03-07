from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.prediction_service import predict_student
from app.auth.dependencies import require_role

router = APIRouter(prefix="/prediction", tags=["Predictions"])


@router.post("/predict/{student_id}/{course_id}")
def run_prediction(student_id: int, course_id: int, db: Session = Depends(get_db)):

    return predict_student(db, student_id, course_id)