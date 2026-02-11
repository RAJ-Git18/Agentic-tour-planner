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
    policy_service,
    tour_planner_service,
    user_services,
    booking_service,
    embedding_service,
    redis_service,
    ranking_service,
    pinecone_service,
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


def get_llm_service(request: Request):
    return request.app.state.llm


def get_pinecone_service():
    return pinecone_service.PineconeService()


def get_embedding_service(request: Request):
    emb_model = request.app.state.emb_model
    return embedding_service.EmbeddingService(model=emb_model)


def get_ranking_service(request: Request):
    cross_encoder = request.app.state.cross_encoder
    return ranking_service.RankingService(model=cross_encoder)


def get_redis_service(request: Request):
    redis_client = request.app.state.redis_client
    return redis_service.RedisService(redis_client=redis_client)


def get_rag_service(
    request: Request,
    embedding_service=Depends(get_embedding_service),
    ranking_service=Depends(get_ranking_service),
    redis_service=Depends(get_redis_service),
):
    pc_index = request.app.state.pc_index
    llm = request.app.state.llm
    embedding_service = embedding_service
    ranking_service = ranking_service
    redis_service = redis_service

    # Core logic: We create the 'dependencies' of RagService here
    policy = policy_service.PolicyService(
        pc_index=pc_index,
        llm=llm,
        embedding_service=embedding_service,
        ranking_service=ranking_service,
        redis_service=redis_service,
    )
    tour = tour_planner_service.TourPlannerService(
        pc_index=pc_index,
        llm=llm,
        embedding_service=embedding_service,
        redis_service=redis_service,
    )

    # Then we inject them into the main service
    return rag_service.RagService(policy_service=policy, tour_planner=tour)


def get_classify_service(request: Request):
    llm = request.app.state.llm
    return classify_services.ClassifyService(llm=llm)


def get_booking_service(request: Request, db: Session = Depends(get_db)):
    return booking_service.BookingService(db=db)


def get_ingest_document(request: Request, pc_service=Depends(get_pinecone_service)):
    pc_index = request.app.state.pc_index
    emb_model = request.app.state.emb_model
    return document_ingestion_service.IngestDocumentService(
        pc_index=pc_index, emb_model=emb_model, pc_service=pc_service
    )


def get_user_services(db: Session = Depends(get_db)):
    return user_services.UserServices(db=db)


def get_graph_config(
    rag_service=Depends(get_rag_service),
    classify_service=Depends(get_classify_service),
    booking_service=Depends(get_booking_service),
    redis_service=Depends(get_redis_service),
):
    return {
        "configurable": {
            "rag_service": rag_service,
            "classify_service": classify_service,
            "booking_service": booking_service,
            "redis_service": redis_service,
        }
    }


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
