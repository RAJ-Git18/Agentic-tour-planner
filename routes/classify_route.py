from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import json
import redis
from workflow.state import GraphState
from workflow.graph import graph
from langchain_core.runnables import RunnableConfig
from utils.logger import logger
from models.models import User
from services.classify_services import ClassifyService
from services.rag_service import RagService
from services.booking_service import BookingService
from services.embedding_service import EmbeddingService
from services.redis_service import RedisService

from dependencies.dependency import (
    get_classify_service,
    get_rag_service,
    get_booking_service,
    get_embedding_service,
    get_redis_service,
)

router = APIRouter(prefix="/api/user-{userid}/classify", tags=["classification"])

# Initialize Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


class UserQuery(BaseModel):
    user_query: str = Field(
        ..., description="Enter the query for the intent classification"
    )


MAX_MESSAGE = 20


@router.post("")
async def classify_user_query(
    userid: int,
    query: UserQuery,
    classify_service: ClassifyService = Depends(get_classify_service),
    rag_service: RagService = Depends(get_rag_service),
    booking_service: BookingService = Depends(get_booking_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    redis_service: RedisService = Depends(get_redis_service),
):
    """
    This starts the graph execution and returns the result.
    """
    session_id = f"session_{userid}"
    user_query = query.user_query

    # Get existing state from Redis
    redis_response = redis_service.get_redis(userid)
    messages = redis_response.get("messages")
    title = redis_response.get("title")

    config = {
        "configurable": {
            "thread_id": session_id,
            "classify_service": classify_service,
            "rag_service": rag_service,
            "booking_service": booking_service,
            "embedding_service": embedding_service,
        }
    }

    # Run the graph
    inputs = {
        "user_id": userid,
        "user_query": user_query,
        "messages": messages,
        "title": title,
    }
    result = await graph.ainvoke(inputs, config=config)
    final_title = result.get("title") or title

    # before setting a key to redis check whether N messages exceeds or not
    redis_service.set_redis(userid=userid, result=result, title=final_title)
    updated_list_of_messages = result.get("messages")
    logger.info(f"Count of messages ----> {len(updated_list_of_messages)}")
    return result
