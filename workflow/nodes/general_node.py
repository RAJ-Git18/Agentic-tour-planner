import json

from workflow.state import GraphState
from langchain_core.runnables import RunnableConfig
from utils.logger import logger


def general_node(state: GraphState, config: RunnableConfig):
    """
    Get the general answer to the user query.
    """
    return {"response": "I am unable to answer your query as this is out of scope."}