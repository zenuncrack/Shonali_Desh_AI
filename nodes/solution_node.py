# nodes/solution_node.py

import json
from state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from llm_client import get_llm

llm = get_llm()


def extract_json(text: str):
    """Extract valid JSON even if model wraps in ``` blocks."""
    if not text:
        return None

    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        try:
            return json.loads(text.replace("'", "\""))
        except:
            return None


def node_plan_solutions(state: AgentState) -> AgentState:

    # STRICT — Array of strings only
    system_prompt = """You are one of Bangladesh’s leading agricultural scientists and an expert in carbon-smart agriculture.

Rules (must be followed with absolute strictness):
- Do not write anything except STRICT VALID JSON.
- Do not write explanations, introductions, or any additional text.
- Do not use markdown.
- Do not use any objects.
- Provide solutions only as an array of "string" items.
- Every solution you provide must be low-cost, environmentally friendly, and supportive of reducing carbon emissions.


Format:

{
  "solutions": [
    "string",
    "string"
  ]
}
"""
    user_payload = json.dumps({
        "problems": state.problems,
        "field_config": state.field_config,
        "iot_data": state.iot_data,
        "satellite_data": state.satellite_data,
        "flood_risk": state.flood_risk,
    })

    # ----------------------
    # FIRST ATTEMPT
    # ----------------------
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_payload),
    ])

    parsed = extract_json(response.content)

    if parsed and "solutions" in parsed and isinstance(parsed["solutions"], list):
        state.solutions = [str(s) for s in parsed["solutions"]]
        return state

    # ----------------------
    # RETRY STRICT
    # ----------------------
    retry_prompt = """
ONLY return strict JSON. No markdown.

If something goes wrong, return:
{"solutions": []}
"""

    retry_response = llm.invoke([
        SystemMessage(content=retry_prompt),
        HumanMessage(content=user_payload),
    ])

    parsed_retry = extract_json(retry_response.content)

    if parsed_retry and "solutions" in parsed_retry:
        sols = parsed_retry["solutions"]
        if isinstance(sols, list):
            state.solutions = [str(s) for s in sols]
        else:
            state.solutions = []
        return state

    # ----------------------
    # FINAL FALLBACK
    # ----------------------
    state.solutions = []
    return state
