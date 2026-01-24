from typing import List, TypedDict, Annotated
from pydantic import Field


class GraphState(TypedDict):
    user_id: int
    user_query: str
    messages: List[dict]
    intent: str
    title: str
    response: str
