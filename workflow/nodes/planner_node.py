import json

from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


def planner_node(state: GraphState, config: RunnableConfig):
    """
    Gets the answer to the user query from the policy document
    """
    logger.info(f"planner node ----> {state}")
    cfg = config.get("configurable")
    user_query = state.get("user_query")
    messages = state.get("messages") or []
    if cfg and user_query:
        rag_service = cfg["rag_service"]
        response = rag_service.tour_planning_service(
            user_query=user_query, message_history=messages
        )
        messages.append({"role": "user", "content": user_query})
        messages.append({"role": "assistant", "content": response})
    else:
        rag_service = None
        raise ValueError("RAG service returned none.")
    return {"response": response, "messages": messages, "title": response["title"]}
