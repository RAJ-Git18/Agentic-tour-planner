from langgraph.graph import StateGraph, START, END
from workflow.state import GraphState
from workflow.nodes.classify_node import classify_node, router_node
from workflow.nodes.policy_node import policy_node
from workflow.nodes.planner_node import planner_node
from workflow.nodes.booking_node import booking_node
from workflow.nodes.general_node import general_node

workflow = StateGraph(GraphState)

# add the nodes here
workflow.add_node("classify", classify_node)
workflow.add_node("policy", policy_node)
workflow.add_node("planning", planner_node)
workflow.add_node("booking", booking_node)
workflow.add_node("general", general_node)

# mention the edges here the workflow
workflow.add_edge(START, "classify")
workflow.add_conditional_edges(
    "classify",
    router_node,
    {
        "policy": "policy",
        "planning": "planning",
        "booking": "booking",
        "general": "general",
    },
)
workflow.add_edge("policy", END)
workflow.add_edge("planning", END)
workflow.add_edge("booking", END)
workflow.add_edge("general", END)

graph = workflow.compile()
