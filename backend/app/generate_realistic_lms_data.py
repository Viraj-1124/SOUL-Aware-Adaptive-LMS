import random
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.assignment import AssignmentSubmission
from app.models.attendance import Attendance
from app.models.activity import StudentActivityLog
from app.models.quiz import QuizAttempt
from app.models.course import Course
from app.models.user import User


db = SessionLocal()

# Example students and courses
student_ids = list(range(1, 21))   # 20 students
course_ids = [1, 2, 3]             # 3 courses

activities = [
    "login",
    "logout",
    "quiz_start",
    "quiz_submit",
    "page_view",
    "video_watch",
    "assignment_open"
]

course_titles = [
    "Data Structures",
    "Machine Learning",
    "Operating Systems",
    "Computer Networks",
    "Database Systems"
]

courses = []

for title in course_titles:

    course = Course(
        title=title,
        description=f"{title} course"
    )

    db.add(course)
    courses.append(course)

db.commit()

for i in range(1, 21):

    student = User(
        email=f"student{i}@test.com",
        password="123456",
        role="STUDENT"
    )

    db.add(student)

db.commit()

for student_id in student_ids:

    for course_id in course_ids:

        # -------------------------
        # Assignment Submissions
        # -------------------------
        for i in range(random.randint(5, 10)):

            submission = AssignmentSubmission(
                student_id=student_id,
                assignment_id=1,
                submission_text="Test submission",
                reflection_text="I struggled with the assignment but improved later.",
                score=random.randint(50, 95),
                submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )

            db.add(submission)

        # -------------------------
        # Quiz Attempts
        # -------------------------
        for i in range(random.randint(5, 8)):

            quiz = QuizAttempt(
                user_id=student_id,
                topic_id=random.randint(1, 3),
                score=random.randint(40, 100),
                total_questions=10,
                time_spent=random.randint(30, 120),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )

            db.add(quiz)

        # -------------------------
        # Activity Logs
        # -------------------------
        for i in range(random.randint(50, 120)):

            activity = StudentActivityLog(
                student_id=student_id,
                course_id=course_id,
                activity_type=random.choice(activities),
                activity_timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                duration_seconds=random.randint(10, 300)
            )

            db.add(activity)

        # -------------------------
        # Attendance
        # -------------------------
        for i in range(20):

            attendance = Attendance(
                student_id=student_id,
                course_id=course_id,
                date=datetime.utcnow().date() - timedelta(days=i),
                present=random.choice([True, False])
            )

            db.add(attendance)

db.commit()
db.close()

print("✅ Test data generated for multiple students and courses.")