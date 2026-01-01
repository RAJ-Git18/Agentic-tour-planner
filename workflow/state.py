from typing import List, TypedDict, Annotated, Union
import operator


class GraphState(TypedDict):
    user_query: str
    messages: List[dict]
    intent: str
    policy_response: str
    planning_response: str
    booking_response: str
    general_response: str
