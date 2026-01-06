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
        if isinstance(existing_state, list):
            messages = existing_state
        else:
            messages = existing_state.get("messages", [])
    else:
        messages = []
        existing_state = {"messages": messages, "user_query": user_query}

    config = {
        "configurable": {
            "thread_id": session_id,
            "rag_service": rag_service,
            "classify_service": classify_service,
            "booking_service": booking_service,
        }
    }

    # Run the graph
    inputs = {"user_id": userid, "user_query": user_query, "messages": messages}
    result = graph.invoke(inputs, config=config)

    # Update Redis state
    redis_client.set(session_id, json.dumps({"messages": result["messages"]}))

    logger.info(f"router ----> {result}")
    return result
