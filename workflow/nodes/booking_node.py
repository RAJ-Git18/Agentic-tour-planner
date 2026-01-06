import json

from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


def booking_node(state: GraphState, config: RunnableConfig):
    """
    confirm the booking of the user as per the plan created
    """
    logger.info(f"booking node ----> {state}")
    cfg = config.get("configurable")
    user_query = state.get("user_query")
    messages = state.get("messages") or []
    if cfg and user_query:
        booking_service = cfg["booking_service"]
        response = booking_service.booking_service(
            user_id=state.get("user_id"),
            planning_response=state.get("planning_response"),
        )
        messages.append({"role": "user", "content": user_query})
        messages.append({"role": "assistant", "content": response})
    else:
        booking_service = None
        raise ValueError("Booking service returned none.")
    return {"booking_response": response}
