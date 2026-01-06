from typing import List, TypedDict, Annotated
from pydantic import Field


class GraphState(TypedDict):
    user_id: int
    user_query: str
    messages: List[dict]
    intent: str
    policy_response: str
    planning_response: str
    booking_response: str
    general_response: str
