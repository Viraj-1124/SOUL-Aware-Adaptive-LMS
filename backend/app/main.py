from fastapi import FastAPI
from .database import engine, SessionLocal
from . import models
from .auth.securities import hash_password
from .routers import users, courses, topics, quizzes, activity

app = FastAPI(title="Soul LMS Backend")

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(topics.router)
app.include_router(quizzes.router)
app.include_router(activity.router)

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