import json

from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


async def general_node(state: GraphState, config: RunnableConfig):
    """
    Get the general answer to the user query.
    """
    return {"response": "I am unable to answer at the moment."}
