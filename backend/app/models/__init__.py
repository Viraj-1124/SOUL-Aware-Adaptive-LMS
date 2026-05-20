from .user import User
from .course import Course, Topic
from .quiz import QuizQuestion, QuizAttempt
from .activity import StudentActivityLog
from .attendance import Attendance
from .assignment import Assignment, AssignmentSubmission
from .knowledge_tracing import StudentQuestionInteraction, StudentKnowledgeState, KnowledgeStateHistory
from .model4_goal_profile import StudentGoalProfile

# This exposes all models so that `from app.models import User` still works elsewhere.
__all__ = [
    "User",
    "Course", "Topic",
    "QuizQuestion", "QuizAttempt",
    "StudentActivityLog",
    "Attendance",
    "Assignment", "AssignmentSubmission",
    "StudentQuestionInteraction", "StudentKnowledgeState", "KnowledgeStateHistory",
    "StudentGoalProfile",
]
