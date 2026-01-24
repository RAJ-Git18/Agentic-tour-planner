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
    title = state.get("title")

    # Fallback: if title is missing from state, look for it in the last assistant message
    if not title:
        for msg in reversed(messages):
            if msg.get("role") == "assistant" and isinstance(msg.get("content"), dict):
                content = msg.get("content")
                if "title" in content:
                    title = content["title"]
                    break

    if not title:
        title = "Planned Tour"  # Final fallback to avoid DB error

    if cfg and user_query:
        booking_service = cfg["booking_service"]
        response = booking_service.booking_service(
            user_id=state.get("user_id"), title=title
        )
        messages.append({"role": "user", "content": user_query})
        messages.append({"role": "assistant", "content": response})
    else:
        booking_service = None
        raise ValueError("Booking service returned none.")
    return {"response": response, "messages": messages, "title": title}
