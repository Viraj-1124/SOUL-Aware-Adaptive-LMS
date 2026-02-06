from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from .. import models, schemas

router = APIRouter(prefix="/activity", tags=["Activity Logs"])


@router.post("/", response_model=schemas.ActivityOut)
def log_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    log = models.ActivityLog(
        user_id=activity.user_id,
        topic_id=activity.topic_id,
        event_type=activity.event_type,
        time_spent=activity.time_spent
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/user/{user_id}")
def get_user_activity(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id
    ).all()


@router.get("/engagement/{user_id}/{topic_id}")
def get_engagement(user_id: int, topic_id: int, db: Session = Depends(get_db)):
    logs = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id,
        models.ActivityLog.topic_id == topic_id
    ).all()

    if not logs:
        return {"engagement_score": 0.0}

    total_time = sum(log.time_spent for log in logs)
    idle_time = sum(
        log.time_spent for log in logs if log.event_type == "idle"
    )

    engagement_score = max(0.0, min(1.0, (total_time - idle_time) / total_time))

    return {
        "engagement_score": round(engagement_score, 2),
        "total_time": total_time,
        "idle_time": idle_time
    }
