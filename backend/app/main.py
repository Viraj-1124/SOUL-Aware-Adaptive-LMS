from fastapi import FastAPI
from .database import engine, SessionLocal, Base
from . import models
from .auth.securities import hash_password
from .routers import attendance, users, courses, topics, quizzes, activity, assignments,learning_health,debug,fatigue,predictions,knowledge

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Soul LMS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(topics.router)
app.include_router(quizzes.router)
app.include_router(activity.router)
app.include_router(attendance.router)
app.include_router(assignments.router)
app.include_router(learning_health.router)
app.include_router(fatigue.router)
app.include_router(predictions.router)
app.include_router(knowledge.router)

@app.get("/")
def root():
    return {"message": "Soul LMS Backend Running"}

@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    admin = db.query(models.User).filter(models.User.role == "ADMIN").first()
    if not admin:
        admin = models.User(
            email ="admin@lms.com",
            password = hash_password("admin123"),
            role="ADMIN"
        )
        db.add(admin)
        db.commit()
    db.close()


@app.on_event("startup")
def create_instructor():
    db = SessionLocal()
    admin = db.query(models.User).filter(models.User.role == "INSTRUCTOR").first()
    if not admin:
        instructor = models.User(
            email ="inst@lms.com",
            password = hash_password("inst123"),
            role="INSTRUCTOR"
        )
        db.add(instructor)
        db.commit()
    db.close()


@app.on_event("startup")
def create_student():
    db = SessionLocal()
    admin = db.query(models.User).filter(models.User.role == "STUDENT").first()
    if not admin:
        student = models.User(
            email ="stud@lms.com",
            password = hash_password("stud123"),
            role="STUDENT"
        )
        db.add(student)
        db.commit()
    db.close()