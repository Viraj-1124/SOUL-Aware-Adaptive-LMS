from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from datetime import datetime
from app.database import Base

class MoralFatigueRecord(Base):
    __tablename__ = "moral_fatigue_records"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    fatigue_score = Column(Integer)
    fatigue_level = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)