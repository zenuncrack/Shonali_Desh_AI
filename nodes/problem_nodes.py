# nodes/problem_nodes.py

import json
from state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from llm_client import get_llm

llm = get_llm()


# -------------------------------------------------------
# JSON extraction helper
# -------------------------------------------------------
def extract_json(text: str):
    """Safely extract valid JSON from LLM output."""
    if not text:
        return None

    # Remove markdown wrappers
    text = text.replace("```json", "").replace("```", "").strip()

    # Try normal parse
    try:
        return json.loads(text)
    except:
        pass

    # Try single-quote repair
    try:
        return json.loads(text.replace("'", "\""))
    except:
        pass

    # Try if model returns:  ["a","b"]  (array only)
    if text.startswith("[") and text.endswith("]"):
        try:
            arr = json.loads(text)
            return {"problems": arr}
        except:
            pass

    return None


# -------------------------------------------------------
# Utility: generate fallback problems automatically
# -------------------------------------------------------
def generate_fallback_problems(state: AgentState):
    problems = []

    # Soil moisture check
    try:
        moisture = state.iot_data.get("latest", {}).get("soilMoisture")
        if moisture is not None and moisture < 20:
            problems.append(f"Soil moisture is low ({moisture}). Irrigation needed.")
    except:
        pass

    # Nitrogen / salinity
    try:
        pred = state.field_config.get("latestPrediction", {})
        if pred.get("nitrogenStatus") == "slightly deficient":
            problems.append("Nitrogen deficiency detected from satellite prediction.")
        if pred.get("salinityRisk") == "moderate":
            problems.append("Moderate salinity risk in the field.")
    except:
        pass

    # Flood risk
    try:
        if state.flood_risk.get("flood_risk") == "high":
            problems.append("High flood risk detected.")
    except:
        pass

    # If still empty → generic fallback
    if not problems:
        problems.append("No specific issues detected, but monitoring recommended.")

    return problems


# -------------------------------------------------------
# Main problem-detection node
# -------------------------------------------------------
def node_detect_problems(state: AgentState) -> AgentState:

    # --- STRICT prompt for STRING-ARRAY ONLY ---
    system_prompt = """
You are an agricultural expert AI.

STRICT RULES:
- Output ONLY STRICT VALID JSON.
- No objects.
- No markdown.
- No explanation.
- Only an array of strings inside "problems".

Format:
{
  "problems": [
    "string",
    "string"
  ]
}
"""

    # Prepare LLM input
    user_payload = json.dumps({
        "field_config": state.field_config,
        "iot_data": state.iot_data,
        "satellite_data": state.satellite_data,
        "flood_risk": state.flood_risk,
    })

    # ---------------------------------------------------
    # FIRST ATTEMPT
    # ---------------------------------------------------
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_payload),
    ])

    parsed = extract_json(response.content)

    if parsed and "problems" in parsed:
        if isinstance(parsed["problems"], list):
            state.problems = [str(p) for p in parsed["problems"]]
            return state

    # ---------------------------------------------------
    # SECOND ATTEMPT (hard retry)
    # ---------------------------------------------------
    retry_prompt = """
Return ONLY valid JSON. STRICT.

If unsure, return:
{"problems": []}
"""

    retry_response = llm.invoke([
        SystemMessage(content=retry_prompt),
        HumanMessage(content=user_payload),
    ])

    parsed_retry = extract_json(retry_response.content)

    if parsed_retry and "problems" in parsed_retry:
        if isinstance(parsed_retry["problems"], list):
            state.problems = [str(p) for p in parsed_retry["problems"]]
            return state

    # ---------------------------------------------------
    # FINAL FALLBACK — generate REAL problems, not empty list
    # ---------------------------------------------------
    state.problems = generate_fallback_problems(state)
    return state
