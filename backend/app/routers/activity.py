from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.activity import ActivityCreate
from app.services.activity_service import log_activity
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/activity", tags=["Activity"])

@router.post("/log")
def log(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return log_activity(db, current_user.id, data)