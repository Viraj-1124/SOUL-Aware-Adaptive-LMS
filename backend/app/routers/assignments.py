#python -m textblob.download_corpora
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AssignmentCreate, AssignmentResponse
from app.schemas import SubmissionCreate, SubmissionResponse
from app.services.submission_service import submit_assignment
from app.auth.dependencies import require_role,get_current_user
from app.models import Assignment

router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.post("/", response_model=AssignmentResponse)
def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "INSTRUCTOR"]))
):
    assignment = Assignment(**data.dict())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

@router.post("/submit", response_model=SubmissionResponse)
def submit(
    data: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["STUDENT"]))
):
    return submit_assignment(db, current_user.id, data)