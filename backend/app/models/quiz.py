from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from datetime import datetime
from app.database import Base

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    question = Column(String)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_option = Column(String)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    topic_id = Column(Integer)
    score = Column(Float)
    total_questions = Column(Integer)
    time_spent = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
