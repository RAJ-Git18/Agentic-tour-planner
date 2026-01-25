from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
import os
import json
import redis
from services.classify_services import ClassifyService
from services.rag_service import RagService
from services.booking_service import BookingService
from dependencies.dependency import (
    get_classify_service,
    get_rag_service,
    get_current_user,
    get_booking_service,
)
from workflow.state import GraphState
from workflow.graph import graph
from langchain_core.runnables import RunnableConfig
from utils.logger import logger
from models.models import User

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
    # current_user: User = Depends(get_current_user),``
):
    # if userid != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Unknow user are not allowed please enter the valid userid path",
    #     )

    session_id = f"session_{userid}"
    user_query = query.user_query

    # Get existing state from Redis
    existing_state_json = redis_client.get(session_id)
    if existing_state_json:
        existing_state = json.loads(existing_state_json)
        if not isinstance(existing_state, dict):
            existing_state = {"messages": existing_state}
    else:
        existing_state = {}

    messages = existing_state.get("messages", [])
    title = existing_state.get("title")

    config = {
        "configurable": {
            "thread_id": session_id,
            "rag_service": rag_service,
            "classify_service": classify_service,
            "booking_service": booking_service,
        }
    }

    # Run the graph
    inputs = {
        "user_id": userid,
        "user_query": user_query,
        "messages": messages,
        "title": title,
    }
    result = graph.invoke(inputs, config=config)
    final_title = result.get("title") or title

    # before setting a key to redis check whether N messages exceeds or not
    if result.get("messages") and len(result.get("messages")) > MAX_MESSAGE:
        updated_list_of_messages = result.get("messages")[-MAX_MESSAGE:]
    else:
        updated_list_of_messages = result.get("messages")

    redis_client.set(
        session_id,
        json.dumps({"messages": updated_list_of_messages, "title": final_title}),
    )
    logger.info(f"Count of messages ----> {len(updated_list_of_messages)}")
    logger.info(f"router ----> {result}")
    return result
