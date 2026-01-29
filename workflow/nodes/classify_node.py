from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


async def classify_node(
    state: GraphState,
    config: RunnableConfig,
):
    """
    Classifies the user query intent.
    """
    cfg = config.get("configurable")
    classify_service = cfg.get("classify_service")
    user_query = state.get("user_query")
    messages = state.get("messages") or []

    if user_query:
        intent = await classify_service.classify(user_query, messages)
    else:
        intent = "general inquiry"

    return {"intent": intent}


def router_node(state: GraphState):
    intent = state.get("intent")
    logger.info(f"router node ----> {intent}")
    if intent == "policy":
        return "policy"
    elif intent == "planning":
        return "planning"
    elif intent == "booking":
        return "booking"
    return "general"
