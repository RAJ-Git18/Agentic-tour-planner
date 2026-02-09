import time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from workflow.state import GraphState
from workflow.graph import graph
from langchain_core.runnables import RunnableConfig
from utils.logger import logger
from models.models import User
from services.classify_services import ClassifyService
from services.redis_service import RedisService

from dependencies.dependency import (
    get_redis_service,
    get_graph_config,
)

router = APIRouter(prefix="/api/user-{userid}/classify", tags=["classification"])


class UserQuery(BaseModel):
    user_query: str = Field(
        ..., description="Enter the query for the intent classification"
    )


MAX_MESSAGE = 20


@router.post("")
async def classify_user_query(
    userid: int,
    query: UserQuery,
    redis_service: RedisService = Depends(get_redis_service),
    config: dict = Depends(get_graph_config),
):
    """
    This starts the graph execution and returns the result.
    """
    session_id = f"session_{userid}"
    user_query = query.user_query
    start_time = time.time()

    # Get existing state from Redis
    redis_response = await redis_service.get_redis(userid)
    messages = redis_response.get("messages")
    title = redis_response.get("title")

    # Add thread_id to the config derived from dependency
    config["configurable"]["thread_id"] = session_id

    # Run the graph
    inputs = {
        "user_id": userid,
        "user_query": user_query,
        "messages": messages,
        "title": title,
    }
    result = await graph.ainvoke(inputs, config=config)
    final_title = result.get("title") or title
    response = result.get("response")

    if response:
        # before setting a key to redis check whether N messages exceeds or not
        await redis_service.set_redis(userid=userid, result=result, title=final_title)
        updated_list_of_messages = result.get("messages")
        logger.info(f"Count of messages ----> {len(updated_list_of_messages)}")
        end_time = time.time()
        logger.info(f"Time taken ----> {end_time - start_time}")
        return result.get("response")

    logger.error("No result from the graph")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="I am unable to answer at the moment. Please try again later.",
    )
