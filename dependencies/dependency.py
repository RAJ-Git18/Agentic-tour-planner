import os
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import Annotated

from services import (
    classify_services,
    document_ingestion_service,
    rag_service,
    user_services,
)
from database.database_setup import SessionLocal
from models.models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_embedding_model(request: Request):
    return request.app.state.emb_model


def get_pinecone_index_service(request: Request):
    return request.app.state.pc_index


def get_llm_service(request: Request):
    return request.app.state.llm


def get_graph(request: Request):
    return request.app.state.graph


def get_rag_service(request: Request):
    pc_index = request.app.state.pc_index
    llm = request.app.state.llm
    return rag_service.RagService(pc_index=pc_index, llm=llm)


def get_classify_service(request: Request):
    emb_model = request.app.state.emb_model
    rag_service_instance = get_rag_service(request)
    llm = request.app.state.llm
    return classify_services.ClassifyService(
        emb_model=emb_model, rag_service=rag_service_instance, llm=llm
    )


def get_ingest_document(request: Request):
    pc_index = request.app.state.pc_index
    emb_model = request.app.state.emb_model
    return document_ingestion_service.IngestDocumentService(
        pc_index=pc_index, emb_model=emb_model
    )


def get_user_services(db: Session = Depends(get_db)):
    return user_services.UserServices(db=db)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userid: str = payload.get("sub")
        if userid is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(userid)).first()
    if user is None:
        raise credentials_exception
    return user


async def get_access_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user not authorized for this endpoint",
        )
    return current_user
