from sqlalchemy.orm import Session
from models.models import User
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from utils.logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

password_hash_helper = PasswordHash.recommended()


class UserServices:
    def __init__(self, db: Session):
        self.db = db

    def get_password_hash(self, password: str):
        return password_hash_helper.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str):
        return password_hash_helper.verify(plain_password, hashed_password)

    def create_user(self, username: str, email: str, password: str):
        if not email:
            raise HTTPException(status_code=400, detail="Invalid email")
        if not password:
            raise HTTPException(status_code=400, detail="Invalid password")

        hashed_password = self.get_password_hash(password)
        db_user = User(username=username, email=email, password_hash=hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def verify_user(self, username: str, password: str):
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
