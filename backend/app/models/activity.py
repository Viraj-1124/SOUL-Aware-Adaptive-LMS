from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class StudentActivityLog(Base):
    __tablename__ = "student_activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    activity_type = Column(String(50), nullable=False)
    activity_timestamp = Column(DateTime, default=datetime.utcnow)

    duration_seconds = Column(Float, nullable=True)

    activity_metadata = Column(String)

    student = relationship("User")
    course = relationship("Course")