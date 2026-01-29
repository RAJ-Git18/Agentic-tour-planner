from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


async def policy_node(
    state: GraphState,
    config: RunnableConfig,
):
    """
    Gets the answer to the user query from the policy document
    """
    cfg = config.get("configurable")
    rag_service = cfg.get("rag_service")
    logger.info(f"policy node ----> {state}")
    user_query = state.get("user_query")

    if rag_service and user_query:
        response = await rag_service.policy_service(user_query)
        return {"response": response}
    else:
        raise ValueError("RAG service returned none.")
