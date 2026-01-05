import json

from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


def confirmation_node(state: GraphState, config: RunnableConfig):
    """
    Gets the answer to the user query from the policy document
    """
    logger.info(f"confirmation node ----> {state}")
    cfg = config.get("configurable")
    user_query = state.get("user_query")
    messages = state.get("messages") or []
    if cfg and user_query:
        confirmation_service = cfg["confirmation_service"]
        response = confirmation_service.confirmation_service(
            user_query=user_query, message_history=messages
        )
        messages.append({"role": "user", "content": user_query})
        messages.append({"role": "assistant", "content": response})
    else:
        confirmation_service = None
        raise ValueError("Confirmation service returned none.")
    return {"is_confirmed": response}


def finish_or_book(state: GraphState, config: RunnableConfig) -> str:
    if state.get("is_confirmed") == True:
        return "book"
    else:
        return "finish"
