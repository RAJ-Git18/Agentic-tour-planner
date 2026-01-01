from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dependencies.dependency import get_db, get_user_services
from services.user_services import UserServices

router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


@router.post("/register")
async def register_user(
    user_data: UserCreate, user_services: UserServices = Depends(get_user_services)
):
    try:
        user = user_services.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )
        return {"message": "User created successfully", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_services: UserServices = Depends(get_user_services),
):
    user = user_services.verify_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_services.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
