from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from .. import models, schemas
from app.auth.dependencies import admin_only, require_role

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=schemas.CourseOut)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(["ADMIN", "INSTRUCTOR"]))
):
    new_course = models.Course(
        title=course.title,
        description=course.description
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/", response_model=list[schemas.CourseOut])
def get_all_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()
