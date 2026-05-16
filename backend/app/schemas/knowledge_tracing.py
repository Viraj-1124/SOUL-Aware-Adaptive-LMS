from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StudentQuestionInteractionCreate(BaseModel):
    topic_id: int
    question_id: int
    attempt_number: int
    correct: bool

class StudentKnowledgeStateOut(BaseModel):
    id: int
    student_id: int
    topic_id: int
    bkt_probability: float
    lstm_probability: float
    mastery_level: str
    last_updated: datetime

    class Config:
        orm_mode = True

class KnowledgePredictionOut(BaseModel):
    student_id: int
    topic_id: int
    bkt_probability: float
    lstm_probability: float
    prediction_correct: bool
    mastery_level: str

class KnowledgeRecommendationOut(BaseModel):
    student_id: int
    topic_id: int
    recommendation: str
    action_item: str
