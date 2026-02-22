from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class StudentSession(Base):
    __tablename__ = "student_sessions"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    login_time = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)

    session_duration = Column(Float, nullable=True)

    student = relationship("User")