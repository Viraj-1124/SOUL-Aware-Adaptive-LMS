from .user import User
from .course import Course, Topic
from .quiz import QuizQuestion, QuizAttempt
from .activity import StudentActivityLog
from .attendance import Attendance
from .assignment import Assignment, AssignmentSubmission

# This exposes all models so that `from app.models import User` still works elsewhere.
__all__ = [
    "User",
    "Course", "Topic",
    "QuizQuestion", "QuizAttempt",
    "StudentActivityLog",
    "Attendance",
    "Assignment", "AssignmentSubmission"
]
