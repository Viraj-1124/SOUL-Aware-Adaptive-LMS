import os
import sys

# Ensure we can import app modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Delete existing lms.db in backend folder
backend_db_path = os.path.join(backend_dir, "lms.db")
if os.path.exists(backend_db_path):
    print(f"Removing existing database at {backend_db_path}...")
    try:
        os.remove(backend_db_path)
        print("Backend database removed.")
    except Exception as e:
        print(f"Error removing backend database: {e}")

# Delete existing lms.db in root folder (just in case)
root_db_path = os.path.join(os.path.dirname(backend_dir), "lms.db")
if os.path.exists(root_db_path):
    print(f"Removing existing database at {root_db_path}...")
    try:
        os.remove(root_db_path)
        print("Root database removed.")
    except Exception as e:
        print(f"Error removing root database: {e}")

# Now import database engine and models
from app.database import Base, engine, SessionLocal
from app.auth.securities import hash_password
from app.models import User, Course, Topic
from app.models.alert import EthicalProfile

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")

db = SessionLocal()

try:
    # 1. Create Default Users
    print("Creating default users...")
    admin = User(
        email="admin@lms.com",
        password=hash_password("admin123"),
        role="ADMIN"
    )
    instructor = User(
        email="inst@lms.com",
        password=hash_password("inst123"),
        role="INSTRUCTOR"
    )
    student = User(
        email="stud@lms.com",
        password=hash_password("stud123"),
        role="STUDENT"
    )
    db.add_all([admin, instructor, student])
    db.commit()
    db.refresh(student)
    print(f"Users created. Student ID: {student.id}")

    # 2. Create Default Courses and Topics
    print("Creating default courses and topics...")
    course1 = Course(
        title="Machine Learning",
        description="Introduction to Machine Learning algorithms and applications."
    )
    course2 = Course(
        title="Data Structures",
        description="Core principles of Data Structures, trees, graphs, and sorting."
    )
    db.add_all([course1, course2])
    db.commit()
    db.refresh(course1)
    db.refresh(course2)

    # Add topics for Machine Learning
    topic1 = Topic(title="Linear Regression", course_id=course1.id)
    topic2 = Topic(title="Neural Networks", course_id=course1.id)
    topic3 = Topic(title="Decision Trees", course_id=course1.id)
    
    # Add topics for Data Structures
    topic4 = Topic(title="Arrays and Linked Lists", course_id=course2.id)
    topic5 = Topic(title="Binary Search Trees", course_id=course2.id)
    topic6 = Topic(title="Graph Algorithms", course_id=course2.id)
    
    db.add_all([topic1, topic2, topic3, topic4, topic5, topic6])
    
    # 3. Create Default Ethical Profile for the student (all clear, 100%)
    print("Creating student ethical profile...")
    profile = EthicalProfile(
        student_id=student.id,
        course_id=course1.id,
        academic_integrity_score=100.0,
        collaboration_fairness_score=100.0,
        self_regulation_score=100.0,
        responsibility_index=100.0,
        integrity_flags=0,
        collaboration_violations=0,
        self_plagiarism_detected=False,
        intervention_sent=False
    )
    db.add(profile)
    
    db.commit()
    print("Database seeding completed successfully!")
    print("No alerts, no remediation modules, no reflection prompts, and no engagement snapshots are populated.")
    print("This ensures that alerts are all clear, remediation and reflection tables are empty, ethics is 100%, and engagement metrics have no data.")

except Exception as e:
    db.rollback()
    print(f"Error seeding database: {e}")
finally:
    db.close()
