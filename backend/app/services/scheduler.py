from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
jobs = {}


def init_scheduler(database_url: str):
    """Initialize scheduler with database connection"""
    from app.models.user import User
    from app.models.course import Course
    from app.services.alert_service import AlertService
    
    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    
    def check_all_student_alerts():
        """Check and create alerts for all active students"""
        try:
            db = SessionLocal()
            
            # Get all active users who are students
            students = db.query(User).filter(
                (User.role == "STUDENT") | (User.role == "LEARNER")
            ).all()
            
            alert_count = 0
            for student in students:
                # Get student's courses
                courses = student.courses if hasattr(student, 'courses') else []
                
                for course in courses:
                    try:
                        alerts = AlertService.check_and_create_alerts(db, student.id, course.id)
                        alert_count += len(alerts)
                    except Exception as e:
                        logger.error(f"Error checking alerts for {student.id} in {course.id}: {e}")
            
            logger.info(f"Alert check completed at {datetime.utcnow()} - Created {alert_count} alerts")
        
        except Exception as e:
            logger.error(f"Error in check_all_student_alerts: {e}")
        finally:
            db.close()
    
    def update_engagement_metrics():
        """Update real-time engagement metrics every hour"""
        try:
            db = SessionLocal()
            from app.services.alert_service import EngagementService
            from app.models.user import User
            from app.models.course import Course
            from app.models.activity import StudentActivityLog
            from sqlalchemy import desc, and_
            from sqlalchemy.sql import func
            
            students = db.query(User).filter(
                (User.role == "STUDENT") | (User.role == "LEARNER")
            ).all()
            
            for student in students:
                courses = student.courses if hasattr(student, 'courses') else []
                
                for course in courses:
                    try:
                        # Calculate engagement metrics
                        hour_ago = datetime.utcnow() - timedelta(hours=1)
                        
                        recent_activities = db.query(StudentActivityLog).filter(
                            and_(
                                StudentActivityLog.student_id == student.id,
                                StudentActivityLog.course_id == course.id,
                                StudentActivityLog.activity_timestamp >= hour_ago
                            )
                        ).all()
                        
                        activity_count = len(recent_activities)
                        avg_response_time = 0
                        
                        if activity_count > 0:
                            response_times = [
                                a.response_time for a in recent_activities 
                                if hasattr(a, 'response_time') and a.response_time
                            ]
                            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                        
                        # Determine trend (simplified)
                        day_ago = datetime.utcnow() - timedelta(days=1)
                        day_activities = db.query(StudentActivityLog).filter(
                            and_(
                                StudentActivityLog.student_id == student.id,
                                StudentActivityLog.course_id == course.id,
                                StudentActivityLog.activity_timestamp >= day_ago
                            )
                        ).count()
                        
                        # Calculate engagement score (0-100)
                        engagement_score = min(100, activity_count * 10 + (100 - avg_response_time))
                        
                        # Determine trend
                        if activity_count > day_activities / 24:
                            trend = "INCREASING"
                        elif activity_count < (day_activities / 24) * 0.5:
                            trend = "DECREASING"
                        else:
                            trend = "STABLE"
                        
                        # Create snapshot
                        EngagementService.create_snapshot(
                            db, student.id, course.id,
                            engagement_score, activity_count, avg_response_time, trend
                        )
                    
                    except Exception as e:
                        logger.error(f"Error updating engagement for {student.id} in {course.id}: {e}")
            
            logger.info(f"Engagement metrics updated at {datetime.utcnow()}")
        
        except Exception as e:
            logger.error(f"Error in update_engagement_metrics: {e}")
        finally:
            db.close()
    
    # Schedule jobs
    try:
        # Check alerts every 6 hours
        job1 = scheduler.add_job(
            check_all_student_alerts,
            'interval',
            hours=6,
            id='check_alerts',
            name='Check and create alerts for all students'
        )
        jobs['check_alerts'] = job1
        logger.info("Scheduled alert checking job (every 6 hours)")
        
        # Update engagement metrics every hour
        job2 = scheduler.add_job(
            update_engagement_metrics,
            'interval',
            hours=1,
            id='update_engagement',
            name='Update real-time engagement metrics'
        )
        jobs['update_engagement'] = job2
        logger.info("Scheduled engagement update job (every 1 hour)")
        
    except Exception as e:
        logger.error(f"Error scheduling jobs: {e}")
    
    return scheduler


def start_scheduler():
    """Start the background scheduler"""
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")


def stop_scheduler():
    """Stop the background scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
