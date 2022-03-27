from typing import List

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from constants import ADMIN
from utils.auth import get_current_user, hash_password, generate_token
from utils.calculations import *
from database import SessionLocal
from crud import user as user_crud
from schemas import user as user_schemas
from schemas import response as response_schemas
from schemas import token as token_schemas


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/users"
)


@router.get("/", response_model=List[user_schemas.User])
async def get_all(db: Session = Depends(get_db), user: user_schemas.User = Depends(get_current_user)):
    if user.nickname == ADMIN:
        users = user_crud.get_users(db)
        return users
    else:
        raise HTTPException(400, "you are not authorized")


@router.post("/register", response_model=response_schemas.Response)
async def register(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """create a new account if nickname was not taken"""
    if user_crud.get_user_by_nickname(db, user.nickname):
        raise HTTPException(401, "nickname is already taken")
    else:
        user_crud.create_user(db, user)
        return {"response": "added user successfully"}


@router.post("/token", response_model=token_schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """login to an existing account"""
    valid_user = user_crud.get_user_by_nickname(db, form_data.username)
    hashed_password = hash_password(form_data.password)
    if valid_user and valid_user.hashed_password == hashed_password:
        return {"access_token": generate_token(valid_user), "token_type": "bearer"}
    else:
        raise HTTPException(401, "wrong nickname or password")