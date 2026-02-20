from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, UniqueConstraint, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="student")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)

    topics = relationship("Topic", back_populates="course")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="topics")


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


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    topic_id = Column(Integer, index=True)
    event_type = Column(String)
    time_spent = Column(Float)  # seconds
    timestamp = Column(DateTime, default=datetime.utcnow)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    date = Column(Date, nullable=False)
    present = Column(Boolean, default=False)

    student = relationship("User")
    course = relationship("Course")

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", "date", name="unique_attendance"),
    )


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