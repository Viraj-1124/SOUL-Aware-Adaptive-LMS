from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from datetime import datetime
from app.database import Base

class StudentPrediction(Base):
    __tablename__ = "student_predictions"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    academic_mastery = Column(Float)
    engagement_score = Column(Float)
    attendance_rate = Column(Float)
    engagement_trend = Column(Float)
    performance_trend = Column(Float)
    attendance_trend = Column(Float)

    risk_level = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)