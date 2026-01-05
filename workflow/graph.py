from langgraph.graph import StateGraph, START, END
from workflow.state import GraphState
from workflow.nodes.classify_node import classify_node, router_node
from workflow.nodes.policy_node import policy_node
from workflow.nodes.planner_node import planner_node
from workflow.nodes.confirmation_node import confirmation_node, finish_or_book

workflow = StateGraph(GraphState)

# add the nodes here
workflow.add_node("classify", classify_node)
workflow.add_node("policy", policy_node)
workflow.add_node("planning", planner_node)
workflow.add_node("confirmation", confirmation_node)
workflow.add_node("booking", finish_or_book)

# mention the edges here the workflow
workflow.add_edge(START, "classify")
workflow.add_conditional_edges(
    "classify", router_node, {"policy": "policy", "planning": "planning"}
)
workflow.add_edge("policy", END)
workflow.add_edge("planning", "confirmation")
workflow.add_edge("confirmation", END)
workflow.add_conditional_edges(
    "confirmation", finish_or_book, {"finish": END, "book": "booking"}
)
workflow.add_edge("booking", END)

graph = workflow.compile()
