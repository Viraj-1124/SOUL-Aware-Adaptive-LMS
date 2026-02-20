from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course")



class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)

    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    submission_text = Column(Text, nullable=False)
    reflection_text = Column(Text, nullable=True)

    score = Column(Float, nullable=True)

    sentiment_score = Column(Float, nullable=True)
    reflection_depth = Column(Float, nullable=True)

    submitted_at = Column(DateTime, default=datetime.utcnow)

    assignment = relationship("Assignment")
    student = relationship("User")
