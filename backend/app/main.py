from fastapi import FastAPI
from .database import engine
from . import models
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
