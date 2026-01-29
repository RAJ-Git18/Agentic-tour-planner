import json

from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


async def planner_node(
    state: GraphState,
    config: RunnableConfig,
):
    """
    Gets the answer to the user query from the policy document
    """
    cfg = config.get("configurable")
    rag_service = cfg.get("rag_service")
    user_query = state.get("user_query")
    messages = state.get("messages") or []
    if rag_service and user_query:
        response = await rag_service.tour_planning_service(
            user_query=user_query, message_history=messages
        )
        messages.append({"role": "user", "content": user_query})
        messages.append({"role": "assistant", "content": response})
    else:
        raise ValueError("RAG service returned none.")
    return {"response": response, "messages": messages, "title": response.get("title")}
