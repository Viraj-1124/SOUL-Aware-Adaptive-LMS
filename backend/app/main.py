from fastapi import FastAPI
from .database import engine
from . import models
from .routers import users

app = FastAPI(title="Soul LMS Backend")

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Soul LMS Backend Running"}
