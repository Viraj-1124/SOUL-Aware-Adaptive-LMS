from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class LearningHealthSnapshot(Base):
    __tablename__ = "learning_health_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    attendance_rate = Column(Float)
    academic_mastery = Column(Float)
    engagement_score = Column(Float)
    sentiment_score = Column(Float)
    reflection_depth = Column(Float)

    health_index = Column(Float)
    risk_level = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User")