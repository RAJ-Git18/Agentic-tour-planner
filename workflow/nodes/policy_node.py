from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


def policy_node(state: GraphState, config: RunnableConfig):
    """
    Gets the answer to the user query from the policy document
    """
    logger.info(f"policy node ----> {state}")
    cfg = config.get("configurable")
    user_query = state.get("user_query")
    rag_service = cfg.get("rag_service")

    if rag_service and user_query:
        response = rag_service.policy_service(user_query)
        return {"response": response}
    else:
        raise ValueError("RAG service returned none.")
