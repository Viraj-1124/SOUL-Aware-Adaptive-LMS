from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from .. import models, schemas

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.post("/", response_model=schemas.TopicOut)
def create_topic(topic: schemas.TopicCreate, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == topic.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_topic = models.Topic(
        title=topic.title,
        course_id=topic.course_id
    )
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic


@router.get("/course/{course_id}", response_model=list[schemas.TopicOut])
def get_topics_by_course(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Topic).filter(models.Topic.course_id == course_id).all()
