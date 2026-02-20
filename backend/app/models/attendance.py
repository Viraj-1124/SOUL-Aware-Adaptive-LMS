from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

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
