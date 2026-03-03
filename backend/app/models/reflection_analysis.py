from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ReflectionAnalysis(Base):
    __tablename__ = "reflection_analysis"

    id = Column(Integer, primary_key=True)

    submission_id = Column(Integer, ForeignKey("assignment_submissions.id"), nullable=False)

    sentiment_polarity = Column(Float)
    sentiment_intensity = Column(Float)

    lexical_diversity = Column(Float)
    self_reference_ratio = Column(Float)
    cognitive_complexity = Column(Float)

    reflection_depth_score = Column(Float)

    emotional_volatility = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("AssignmentSubmission")