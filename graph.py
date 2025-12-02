# graph.py

from langgraph.graph import StateGraph, END
from state import AgentState

from nodes.fetch_nodes import (
    node_fetch_field_and_farmer,
    node_fetch_iot,
    node_fetch_satellite,
    node_fetch_carbon,
    node_fetch_flood,
)

from nodes.problem_nodes import node_detect_problems
from nodes.solution_node import node_plan_solutions
from tools.firebase_tools import save_agent_output_tool


def node_save_output(state: AgentState) -> AgentState:
    """Save problems + solutions + carbon into Firebase"""

    save_agent_output_tool.invoke({
        "farmer_id": state.farmer_id,
        "field_id": state.field_id,
        "problems": state.problems or [],
        "solutions": state.solutions or [],
        "carbon_data": state.carbon_data or None
    })

    return state


# ---------------------------------------------------------
# Build LangGraph Pipeline
# ---------------------------------------------------------
builder = StateGraph(AgentState)

# Register nodes
builder.add_node("fetch_field_and_farmer", node_fetch_field_and_farmer)
builder.add_node("fetch_iot", node_fetch_iot)
builder.add_node("fetch_satellite", node_fetch_satellite)
builder.add_node("fetch_carbon", node_fetch_carbon)
builder.add_node("fetch_flood", node_fetch_flood)
builder.add_node("detect_problems", node_detect_problems)
builder.add_node("plan_solutions", node_plan_solutions)
builder.add_node("save_output", node_save_output)

# Entry point
builder.set_entry_point("fetch_field_and_farmer")

# Pipeline edges (execution order)
builder.add_edge("fetch_field_and_farmer", "fetch_iot")
builder.add_edge("fetch_iot", "fetch_satellite")
builder.add_edge("fetch_satellite", "fetch_carbon")   # NEW
builder.add_edge("fetch_carbon", "fetch_flood")
builder.add_edge("fetch_flood", "detect_problems")
builder.add_edge("detect_problems", "plan_solutions")
builder.add_edge("plan_solutions", "save_output")
builder.add_edge("save_output", END)

# Compile graph
field_agent_graph = builder.compile()
