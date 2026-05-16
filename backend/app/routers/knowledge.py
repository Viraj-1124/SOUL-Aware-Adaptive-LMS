from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.knowledge_tracing import KnowledgeService
from app.schemas.knowledge_tracing import StudentKnowledgeStateOut, KnowledgePredictionOut, KnowledgeRecommendationOut

router = APIRouter(prefix="/knowledge", tags=["Knowledge Tracing"])

@router.get("/state/{student_id}", response_model=List[StudentKnowledgeStateOut])
def get_knowledge_state(student_id: int, db: Session = Depends(get_db)):
    """
    Get the current knowledge state across all topics for a student.
    """
    states = KnowledgeService.get_knowledge_state(db, student_id)
    return states

@router.get("/predict/{student_id}", response_model=List[KnowledgePredictionOut])
def predict_performance(student_id: int, db: Session = Depends(get_db)):
    """
    Get mastery prediction and next-answer correctness probability for a student.
    """
    states = KnowledgeService.get_knowledge_state(db, student_id)
    predictions = []
    for state in states:
        predictions.append(
            KnowledgePredictionOut(
                student_id=state.student_id,
                topic_id=state.topic_id,
                bkt_probability=state.bkt_probability,
                lstm_probability=state.lstm_probability,
                prediction_correct=state.bkt_probability > 0.5 or state.lstm_probability > 0.5,
                mastery_level=state.mastery_level
            )
        )
    return predictions

@router.get("/recommendation/{student_id}/{topic_id}", response_model=KnowledgeRecommendationOut)
def get_topic_recommendation(student_id: int, topic_id: int, db: Session = Depends(get_db)):
    """
    Get an adaptive learning recommendation for a specific student and topic.
    """
    rec = KnowledgeService.get_recommendation(db, student_id, topic_id)
    return KnowledgeRecommendationOut(**rec)
