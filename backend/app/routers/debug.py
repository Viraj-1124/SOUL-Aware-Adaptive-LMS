from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.feature_engineering import build_feature_vector

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/features/{student_id}/{course_id}")
def get_features(student_id: int, course_id: int, db: Session = Depends(get_db)):
    features = build_feature_vector(db, student_id, course_id)
    return {
        "academic_mastery": features[0],
        "engagement_score": features[1],
        "attendance_rate": features[2],
        "engagement_trend": features[3],
        "performance_trend": features[4],
        "attendance_trend": features[5]
    }