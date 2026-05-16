import random
from datetime import datetime, timedelta
import sys
import os

# Ensure we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.knowledge_tracing import StudentQuestionInteraction, StudentKnowledgeState, KnowledgeStateHistory
from app.knowledge_tracing.knowledge_service import KnowledgeService
from app.models.user import User

db = SessionLocal()

def seed_knowledge_tracing():
    # Make sure we have some users
    users = db.query(User).filter(User.role == "STUDENT").limit(5).all()
    if not users:
        print("No student users found to seed data for.")
        return

    print(f"Seeding knowledge tracing data for {len(users)} students...")

    # Clear existing KT data to avoid duplicates/confusion during test
    db.query(StudentKnowledgeState).delete()
    db.query(KnowledgeStateHistory).delete()
    db.query(StudentQuestionInteraction).delete()
    db.commit()

    topics = [1, 2, 3] # Sample topics

    for idx, student in enumerate(users):
        student_id = student.id
        
        # Determine student profile based on idx to get varying recommendations
        if idx == 0:
            profile = "advanced" # 90% chance correct
        elif idx == 1:
            profile = "struggling" # 30% chance correct
        else:
            profile = "intermediate" # 60% chance correct

        for topic_id in topics:
            num_questions = random.randint(10, 15)
            
            for q_idx in range(num_questions):
                if profile == "advanced":
                    correct = random.random() < 0.90
                elif profile == "struggling":
                    correct = random.random() < 0.30
                else:
                    correct = random.random() < 0.60
                
                # Question ID 1-50
                question_id = random.randint(1, 50)
                
                interaction = StudentQuestionInteraction(
                    student_id=student_id,
                    topic_id=topic_id,
                    question_id=question_id,
                    attempt_number=1, # simplified
                    correct=correct,
                    created_at=datetime.utcnow() - timedelta(days=2, hours=random.randint(1, 24))
                )
                db.add(interaction)
                
            db.commit()
            
            # Now trigger the service to compute the state from these interactions
            try:
                KnowledgeService.process_quiz_submission(db, student_id, topic_id)
            except Exception as e:
                print(f"Failed to process for student {student_id}, topic {topic_id}: {e}")

    print("✅ Knowledge Tracing seeding complete!")
    
    # Print out a summary to help the user
    print("\nUse the following Student IDs to test different outcomes:")
    for idx, student in enumerate(users):
        if idx == 0:
            print(f"- Student {student.id} (Advanced - Expect High probabilities / 'Advanced' recommendation)")
        elif idx == 1:
            print(f"- Student {student.id} (Struggling - Expect Low probabilities / 'Remediation' recommendation)")
        else:
            print(f"- Student {student.id} (Intermediate - Expect Mid probabilities / 'Normal' recommendation)")

if __name__ == "__main__":
    seed_knowledge_tracing()
