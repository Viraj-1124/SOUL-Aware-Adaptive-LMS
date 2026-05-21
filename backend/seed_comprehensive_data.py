import os
import sys
import random
import json
from datetime import datetime, timedelta

# Ensure we can import app modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Terminate existing connections by removing the SQLite database file
backend_db_path = os.path.join(backend_dir, "lms.db")
if os.path.exists(backend_db_path):
    print(f"Removing existing database at {backend_db_path}...")
    try:
        os.remove(backend_db_path)
        print("Backend database removed.")
    except Exception as e:
        print(f"Error removing backend database: {e}")

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

from app.models import User, Course, Topic, QuizQuestion, QuizAttempt, Attendance, Assignment, AssignmentSubmission, StudentActivityLog
from app.models.alert import AlertRule, StudentAlert, AlertLog, RemediationModule, ReflectionPrompt, EthicalProfile, CurriculumSequence, EngagementSnapshot
from app.models.moral_fatigue_record import MoralFatigueRecord
from app.models.student_prediction import StudentPrediction
from app.models.learning_health_snapshot import LearningHealthSnapshot
from app.models.reflection_analysis import ReflectionAnalysis
from app.models.knowledge_tracing import StudentQuestionInteraction, StudentKnowledgeState, KnowledgeStateHistory
from app.models.model4_goal_profile import StudentGoalProfile

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully.")

db = SessionLocal()

try:
    # 1. Create Default and Mock Users
    print("Seeding users...")
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
    # The primary demo student (needs clean state output)
    demo_student = User(
        email="stud@lms.com",
        password=hash_password("stud123"),
        role="STUDENT"
    )
    db.add_all([admin, instructor, demo_student])
    
    # 20 synthetic students for ML/fatigue/KBT algorithms
    students = []
    for i in range(1, 21):
        stud = User(
            email=f"student{i}@test.com",
            password=hash_password("stud123"),
            role="STUDENT"
        )
        db.add(stud)
        students.append(stud)
    
    db.commit()
    
    # Refresh to retrieve generated database IDs
    db.refresh(demo_student)
    for s in students:
        db.refresh(s)
        
    all_student_ids = [demo_student.id] + [s.id for s in students]
    mock_student_ids = [s.id for s in students]
    
    print(f"Users seeded. Admin: {admin.id}, Instructor: {instructor.id}, Demo Student: {demo_student.id}, Mock Students: {len(students)}")

    # 2. Create Courses and Topics
    print("Seeding courses and topics...")
    course_data = [
        {
            "title": "Machine Learning",
            "desc": "Introduction to Machine Learning algorithms, optimization, and implementations.",
            "topics": ["Linear Regression", "Neural Networks", "Decision Trees", "Support Vector Machines", "Clustering"]
        },
        {
            "title": "Data Structures",
            "desc": "Core concepts of data organization, trees, graphs, sorting, and algorithmic analysis.",
            "topics": ["Arrays and Linked Lists", "Binary Search Trees", "Graph Algorithms", "Heaps and Priority Queues", "Hash Tables"]
        },
        {
            "title": "Operating Systems",
            "desc": "Foundational course on process scheduling, virtual memory, deadlocks, and virtualization.",
            "topics": ["Process Scheduling", "Memory Management", "File Systems", "Deadlock Resolution", "Virtual Machines"]
        },
        {
            "title": "Computer Networks",
            "desc": "Detailed analysis of transport protocols, routing algorithms, DNS, and wireless communications.",
            "topics": ["TCP/IP Protocol Suite", "Routing Algorithms", "Domain Name System", "Network Security Protocols", "Wireless LANs"]
        },
        {
            "title": "Database Systems",
            "desc": "Relational query analysis, relational algebra, indices, and transaction processing.",
            "topics": ["Relational Algebra", "SQL Queries", "Normal Forms", "Indexing and Hashing", "Transaction Management"]
        }
    ]

    courses = []
    topics = {}
    for c_info in course_data:
        course = Course(title=c_info["title"], description=c_info["desc"])
        db.add(course)
        db.commit()
        db.refresh(course)
        courses.append(course)
        
        topics[course.id] = []
        for t_title in c_info["topics"]:
            topic = Topic(title=t_title, course_id=course.id)
            db.add(topic)
            db.commit()
            db.refresh(topic)
            topics[course.id].append(topic)
            
            # Create Quiz Questions for each topic
            for q_idx in range(1, 6):
                question = QuizQuestion(
                    topic_id=topic.id,
                    question=f"Question {q_idx} for {topic.title}?",
                    option_a="Option A",
                    option_b="Option B",
                    option_c="Option C",
                    option_d="Option D",
                    correct_option="Option A"
                )
                db.add(question)
                
    db.commit()
    print("Courses, topics, and quiz questions seeded successfully.")

    # 3. Create Assignments
    print("Seeding assignments...")
    assignments = []
    for course in courses:
        for a_idx in range(1, 4):
            assignment = Assignment(
                course_id=course.id,
                title=f"{course.title} Assignment {a_idx}",
                description=f"Detailed tasks for {course.title} assignment number {a_idx}.",
                due_date=datetime.utcnow() + timedelta(days=a_idx * 7)
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            assignments.append(assignment)
            
    print("Assignments seeded.")

    # 4. Seeding Data for Mock Students (IDs 4 to 23)
    # Note: We omit demo_student (ID 3) here to ensure their dashboard remains clean,
    # except for basic structural assignments/attendance where needed for course screens.
    print("Seeding metrics, attempts, activities, and logs for synthetic dataset...")
    activity_types = ["login", "logout", "quiz_start", "quiz_submit", "page_view", "video_watch", "assignment_open"]
    
    # Track student metrics to seed predictions and health snapshots
    student_stats = {}
    
    for s_id in all_student_ids:
        student_stats[s_id] = {
            "submissions": 0,
            "total_score": 0,
            "quiz_attempts": 0,
            "quiz_score": 0,
            "activities": 0,
            "attendance_present": 0,
            "attendance_total": 0
        }

    # Generate logs, attempts, submissions, and attendance
    for s_id in all_student_ids:
        # Check if this is the demo student
        is_demo = (s_id == demo_student.id)
        
        for course in courses:
            # A. Attendance (last 30 days)
            presence_rate = 1.0 if is_demo else random.choice([0.65, 0.75, 0.85, 0.95])
            for d in range(30):
                present = (random.random() < presence_rate)
                att = Attendance(
                    student_id=s_id,
                    course_id=course.id,
                    date=datetime.utcnow().date() - timedelta(days=d),
                    present=present
                )
                db.add(att)
                student_stats[s_id]["attendance_total"] += 1
                if present:
                    student_stats[s_id]["attendance_present"] += 1

            # Skip generating performance data for demo student to keep dashboards clear
            if is_demo:
                continue

            # B. Assignment Submissions
            course_assignments = [a for a in assignments if a.course_id == course.id]
            for assign in course_assignments:
                score = random.randint(55, 98)
                sub = AssignmentSubmission(
                    student_id=s_id,
                    assignment_id=assign.id,
                    submission_text=f"Submission details for assignment {assign.title}.",
                    reflection_text=f"I spent several hours on this. The topic was interesting but challenging.",
                    score=score,
                    submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
                )
                db.add(sub)
                db.commit()
                db.refresh(sub)
                student_stats[s_id]["submissions"] += 1
                student_stats[s_id]["total_score"] += score
                
                # Create Reflection Analysis
                ref_analysis = ReflectionAnalysis(
                    submission_id=sub.id,
                    sentiment_polarity=random.choice([-0.2, 0.1, 0.4, 0.6]),
                    sentiment_intensity=random.random(),
                    lexical_diversity=random.uniform(0.4, 0.8),
                    self_reference_ratio=random.uniform(0.05, 0.25),
                    cognitive_complexity=random.uniform(0.3, 0.9),
                    reflection_depth_score=random.uniform(50.0, 95.0),
                    emotional_volatility=random.uniform(0.0, 0.3)
                )
                db.add(ref_analysis)

            # C. Quiz Attempts and Interactions (for Knowledge Tracing)
            course_topics = topics[course.id]
            for topic in course_topics:
                # 2 attempts per topic
                for attempt_no in range(1, 3):
                    score = random.randint(40, 100)
                    attempt = QuizAttempt(
                        user_id=s_id,
                        topic_id=topic.id,
                        score=score,
                        total_questions=5,
                        time_spent=random.randint(45, 300),
                        timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 20))
                    )
                    db.add(attempt)
                    student_stats[s_id]["quiz_attempts"] += 1
                    student_stats[s_id]["quiz_score"] += score
                    
                # Question interactions for KBT model training
                for q_idx in range(1, 6):
                    correct = (random.random() < 0.70)
                    interaction = StudentQuestionInteraction(
                        student_id=s_id,
                        topic_id=topic.id,
                        question_id=random.randint(1, 100),
                        attempt_number=1,
                        correct=correct,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
                    )
                    db.add(interaction)

            # D. Activity Logs (last 30 days)
            num_logs = random.randint(80, 150)
            for _ in range(num_logs):
                act_type = random.choice(activity_types)
                act = StudentActivityLog(
                    student_id=s_id,
                    course_id=course.id,
                    activity_type=act_type,
                    activity_timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 25), hours=random.randint(0, 23)),
                    duration_seconds=random.randint(15, 600)
                )
                db.add(act)
                student_stats[s_id]["activities"] += 1

            # E. Moral Fatigue Records
            for d in range(10):
                score = random.randint(15, 85)
                level = "LOW" if score < 40 else ("MEDIUM" if score < 70 else "HIGH")
                fatigue = MoralFatigueRecord(
                    student_id=s_id,
                    course_id=course.id,
                    fatigue_score=score,
                    fatigue_level=level,
                    created_at=datetime.utcnow() - timedelta(days=d)
                )
                db.add(fatigue)

            # F. Student Predictions
            mastery = random.uniform(50.0, 95.0)
            engagement = random.uniform(40.0, 90.0)
            att_rate = presence_rate * 100
            risk = 2 if (mastery < 60 and engagement < 50) else (1 if (mastery < 70 or engagement < 60) else 0)
            
            prediction = StudentPrediction(
                student_id=s_id,
                course_id=course.id,
                academic_mastery=mastery,
                engagement_score=engagement,
                attendance_rate=att_rate,
                engagement_trend=random.uniform(-10.0, 10.0),
                performance_trend=random.uniform(-5.0, 15.0),
                attendance_trend=random.uniform(-5.0, 5.0),
                risk_level=risk,
                burnout_probability=0.85 if risk == 2 else (0.50 if risk == 1 else 0.15),
                created_at=datetime.utcnow()
            )
            db.add(prediction)

            # G. Engagement Snapshots (for trend graphs)
            for h in range(24):
                snap = EngagementSnapshot(
                    student_id=s_id,
                    course_id=course.id,
                    engagement_score=random.uniform(45.0, 95.0),
                    activity_count=random.randint(5, 25),
                    avg_response_time=random.uniform(1.5, 6.0),
                    engagement_trend=random.choice(["INCREASING", "STABLE", "DECREASING"]),
                    timestamp=datetime.utcnow() - timedelta(hours=h)
                )
                db.add(snap)

    db.commit()
    print("Performance metrics, quiz attempts, activity logs, fatigue scores, and predictions seeded.")

    # 5. Seeding Learning Health Snapshots for all students
    print("Seeding learning health snapshots...")
    for s_id in all_student_ids:
        stats = student_stats[s_id]
        
        att_rate = (stats["attendance_present"] / stats["attendance_total"]) if stats["attendance_total"] > 0 else 1.0
        mastery = (stats["total_score"] / stats["submissions"]) if stats["submissions"] > 0 else 85.0
        eng_score = min(100.0, max(0.0, stats["activities"] / 10.0)) if s_id != demo_student.id else 0.0
        
        health = LearningHealthSnapshot(
            student_id=s_id,
            attendance_rate=att_rate * 100.0,
            academic_mastery=mastery,
            engagement_score=eng_score,
            sentiment_score=random.uniform(0.1, 0.7) if s_id != demo_student.id else 0.5,
            reflection_depth=random.uniform(50.0, 90.0) if s_id != demo_student.id else 0.0,
            health_index=random.uniform(65.0, 98.0) if s_id != demo_student.id else 100.0,
            risk_level=0 if s_id == demo_student.id else random.choice([0, 1, 2])
        )
        db.add(health)
    db.commit()

    # 6. Seed Knowledge States for all students
    print("Seeding Knowledge States...")
    for s_id in all_student_ids:
        for course in courses:
            course_topics = topics[course.id]
            for topic in course_topics:
                # Seed knowledge state
                bkt_val = 0.95 if s_id == demo_student.id else random.uniform(0.3, 0.9)
                lstm_val = min(1.0, max(0.0, bkt_val + random.uniform(-0.05, 0.05)))
                mastery = "Mastered" if bkt_val >= 0.8 else ("Intermediate" if bkt_val >= 0.5 else "Beginner")
                state = StudentKnowledgeState(
                    student_id=s_id,
                    topic_id=topic.id,
                    bkt_probability=bkt_val,
                    lstm_probability=lstm_val,
                    mastery_level=mastery,
                    last_updated=datetime.utcnow()
                )
                db.add(state)
                db.commit()
                db.refresh(state)
                
                # Seed history
                history = KnowledgeStateHistory(
                    student_id=s_id,
                    topic_id=topic.id,
                    bkt_probability=state.bkt_probability,
                    lstm_probability=state.lstm_probability,
                    mastery_level=state.mastery_level,
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
                db.add(history)
    db.commit()

    # 7. Seeding Ethical Profiles
    print("Seeding ethical profiles...")
    for s_id in all_student_ids:
        is_demo = (s_id == demo_student.id)
        
        profile = EthicalProfile(
            student_id=s_id,
            course_id=courses[0].id,
            academic_integrity_score=100.0 if is_demo else random.choice([70.0, 80.0, 90.0, 100.0]),
            collaboration_fairness_score=100.0 if is_demo else random.uniform(65.0, 100.0),
            self_regulation_score=100.0 if is_demo else random.uniform(70.0, 100.0),
            responsibility_index=100.0 if is_demo else random.uniform(60.0, 100.0),
            integrity_flags=0 if is_demo else random.choice([0, 1, 2]),
            collaboration_violations=0 if is_demo else random.choice([0, 1]),
            self_plagiarism_detected=False if is_demo else (random.random() < 0.2),
            intervention_sent=False
        )
        db.add(profile)
    db.commit()
    print("Ethical profiles seeded.")

    # 8. Seeding Alerts, Alert Rules, Remediation Modules, and Reflection Prompts
    print("Seeding alerts and remediation components...")
    
    # Default alert rules for all students and courses
    for s_id in all_student_ids:
        is_demo = (s_id == demo_student.id)
        
        for course in courses:
            # Rules
            rule1 = AlertRule(
                student_id=s_id,
                course_id=course.id,
                alert_type="FATIGUE",
                trigger_metric="fatigue_score",
                threshold=75.0,
                operator=">=",
                severity="HIGH",
                message_template="Moral fatigue threshold exceeded: {metric_value}",
                active=True
            )
            rule2 = AlertRule(
                student_id=s_id,
                course_id=course.id,
                alert_type="PERFORMANCE",
                trigger_metric="academic_mastery",
                threshold=60.0,
                operator="<",
                severity="CRITICAL",
                message_template="Academic mastery dropped to {metric_value}%",
                active=True
            )
            db.add_all([rule1, rule2])
            db.commit()
            db.refresh(rule1)
            db.refresh(rule2)
            
            # Seed alerts and remediation for synthetic students (omitting demo_student to keep it clean)
            if is_demo:
                continue
                
            # Create a mock alert
            if random.random() < 0.4:
                alert = StudentAlert(
                    rule_id=rule1.id,
                    student_id=s_id,
                    alert_type="FATIGUE",
                    severity="HIGH",
                    title="High Fatigue Detected",
                    message="AI model detected excessive session durations and rapid inputs indicating exhaustion.",
                    metric_value=82.0,
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
                db.add(alert)
                db.commit()
                db.refresh(alert)
                
                # Acknowledged alerts in history
                ack_alert = StudentAlert(
                    rule_id=rule2.id,
                    student_id=s_id,
                    alert_type="PERFORMANCE",
                    severity="CRITICAL",
                    title="Academic Mastery drop",
                    message="Student scored low in consecutive quiz assessments.",
                    metric_value=54.5,
                    created_at=datetime.utcnow() - timedelta(days=5),
                    acknowledged_at=datetime.utcnow() - timedelta(days=4),
                    acknowledged_by_id=2, # Instructor
                    dismissal_reason="Assigned remediation modules."
                )
                db.add(ack_alert)
                
                # Create a remediation module
                module = RemediationModule(
                    student_id=s_id,
                    course_id=course.id,
                    title="Remedial Session: Concepts Alignment",
                    description="Personalized module addressing concepts in Linear Regression.",
                    skill_gap="Linear Regression",
                    difficulty_level="BEGINNER",
                    content="Linear regression is a linear approach for modelling the relationship between a scalar response and one or more explanatory variables.",
                    content_type="TEXT",
                    generated_by="LLM_OPENAI",
                    completion_percentage=40.0,
                    assigned_at=datetime.utcnow() - timedelta(days=2)
                )
                db.add(module)
                db.commit()
                db.refresh(module)
                
                # Create reflection prompt
                prompt = ReflectionPrompt(
                    student_id=s_id,
                    module_id=module.id,
                    prompt_text="What was the most challenging aspect of implementing Linear Regression, and how did you resolve it?",
                    context="SKILL_GAP",
                    generated_at=datetime.utcnow() - timedelta(days=1)
                )
                db.add(prompt)

    # 9. Seeding Goal Profiles
    print("Seeding student goal profiles...")
    mock_goals = [
        "I want to become a full stack developer and build modern responsive web applications.",
        "I want to learn machine learning algorithms and implement deep learning neural networks.",
        "I want to master database systems and server-side backend development.",
        "I want to prepare for competitive coding contests by mastering advanced data structures and graph algorithms.",
        "I want to build highly scalable microservices and learn docker, kubernetes, and DevOps.",
    ]
    domains = ["frontend", "ml", "backend", "dsa", "devops"]
    
    for idx, s_id in enumerate(mock_student_ids):
        goal_text = mock_goals[idx % len(mock_goals)]
        pred_domain = domains[idx % len(domains)]
        
        # Build domain scores
        dom_scores = {d: 0.1 for d in domains}
        dom_scores[pred_domain] = 0.85
        
        skill_gaps = {
            "html_mastery": random.uniform(0.1, 0.4),
            "css_mastery": random.uniform(0.1, 0.4),
            "js_mastery": random.uniform(0.1, 0.5),
            "react_mastery": random.uniform(0.2, 0.6),
            "python_mastery": random.uniform(0.1, 0.5),
            "ml_mastery": random.uniform(0.3, 0.7),
            "dsa_mastery": random.uniform(0.2, 0.6),
        }
        
        profile = StudentGoalProfile(
            student_id=s_id,
            goal_text=goal_text,
            goal_type="career" if "become" in goal_text else "learning",
            goal_specificity_score=random.uniform(0.65, 0.95),
            goal_embedding=json.dumps([random.uniform(-0.1, 0.1) for _ in range(384)]),
            
            html_mastery=random.uniform(0.5, 0.9),
            css_mastery=random.uniform(0.5, 0.9),
            js_mastery=random.uniform(0.5, 0.9),
            react_mastery=random.uniform(0.3, 0.8),
            python_mastery=random.uniform(0.4, 0.8),
            ml_mastery=random.uniform(0.2, 0.7),
            dsa_mastery=random.uniform(0.3, 0.7),
            
            environment=random.choice(["online", "lab", "project", "self-study"]),
            engagement_score=random.uniform(0.5, 0.9),
            consistency_score=random.uniform(0.5, 0.9),
            integrity_score=random.uniform(0.6, 1.0),
            anomaly_score=random.uniform(0.01, 0.15),
            collaboration_score=random.uniform(0.5, 0.95),
            
            alignment_score=random.uniform(0.65, 0.95),
            predicted_domain=pred_domain,
            all_domain_scores=json.dumps(dom_scores),
            
            skill_gap=sum(skill_gaps.values()) / len(skill_gaps),
            skill_gap_vector=json.dumps(skill_gaps),
            weakest_topics=json.dumps(["Linear Regression", "Graph Algorithms", "Memory Management"]),
            
            context_adjustment_score=random.uniform(0.05, 0.2),
            learning_mode_hint=random.choice(["interactive", "project-based", "visual"]),
            integrity_flag=False,
            scaffold_level=random.choice(["low", "medium", "high"]),
            behavior_summary="Stable engagement with minor pacing adjustments.",
            
            recommendation=f"Recommended path for {pred_domain.upper()}: focus on key gaps in JavaScript/ML.",
            learning_path=json.dumps([
                f"Master foundational concepts in {pred_domain}",
                "Work on practical project implementations",
                "Complete assessments with score > 80%"
            ]),
            resources=json.dumps([
                f"Advanced guide to {pred_domain}",
                f"Hands-on exercises for {pred_domain} concepts"
            ]),
            explanation=f"Matches {pred_domain} profile based on current metrics.",
            confidence_score=random.uniform(0.75, 0.95)
        )
        db.add(profile)

    db.commit()
    print("Database seeding successfully completed!")
    print("\nSUMMARY:")
    print("1. All database tables are fully populated with rich mock datasets across 20 synthetic students.")
    print("2. Models (Fatigue, KBT, Predictions) have ample data to read and run analytics.")
    print("3. Demo Student (stud@lms.com) has clean records: no active alerts, no remediation, no reflection, and 100% ethics.")
    
except Exception as e:
    db.rollback()
    print(f"Error seeding database: {e}")
finally:
    db.close()
