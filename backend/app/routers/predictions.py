from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.services.prediction_service import predict_student
from app.auth.dependencies import require_role

router = APIRouter(prefix="/prediction", tags=["Predictions"])


@router.post("/predict/{student_id}/{course_id}")
def run_prediction(student_id: int, course_id: int, db: Session = Depends(get_db)):

    return predict_student(db, student_id, course_id)

@router.get("/run-for-all-students")
def run_prediction_for_all_students(db: Session = Depends(get_db)):

    students = db.query(User).filter(User.role == "STUDENT").all()
    courses = db.query(Course).all()

    results = []

    risk_count = {
        "low_risk": 0,
        "medium_risk": 0,
        "high_risk": 0
    }

    for student in students:
        for course in courses:

            try:
                prediction = predict_student(db, student.id, course.id)

                risk_level = prediction["risk_level"]

                if risk_level == 0:
                    risk = "low_risk"
                elif risk_level == 1:
                    risk = "medium_risk"
                else:
                    risk = "high_risk"

                risk_count[risk] += 1

                results.append({
                    "student_id": student.id,
                    "course_id": course.id,
                    "risk_level": risk
                })

            except:
                continue

    return {
        "summary": risk_count,
        "results": results
    }