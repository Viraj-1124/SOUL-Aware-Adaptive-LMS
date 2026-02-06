from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal,get_db
from .. import models, schemas
from app.auth.securities import hash_password, verify_password
from app.auth.jwt import create_access_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    new_user = models.User(
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
