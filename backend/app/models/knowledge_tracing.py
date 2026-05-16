from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from datetime import datetime
from app.database import Base

class StudentQuestionInteraction(Base):
    __tablename__ = "student_question_interactions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    question_id = Column(Integer, ForeignKey("quiz_questions.id"))
    attempt_number = Column(Integer)
    correct = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentKnowledgeState(Base):
    __tablename__ = "student_knowledge_states"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    bkt_probability = Column(Float)
    lstm_probability = Column(Float)
    mastery_level = Column(String)  # e.g., "Beginner", "Intermediate", "Mastered"
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeStateHistory(Base):
    __tablename__ = "knowledge_state_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    bkt_probability = Column(Float)
    lstm_probability = Column(Float)
    mastery_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
