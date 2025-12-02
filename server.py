# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from graph import field_agent_graph
from state import AgentState
from langserve import add_routes
import uvicorn

app = FastAPI(title="Field Guardian AI Agent")

class Request(BaseModel):
    farmer_id: str
    field_id: str


@app.post("/run_once")
def run_once(req: Request):
    initial: AgentState = {
        "farmer_id": req.farmer_id,
        "field_id": req.field_id,
    }
    result = field_agent_graph.invoke(initial)
    return {
        "problems": result.get("problems", []),
        "solutions": result.get("solutions", []),
    }

# LangGraph API
add_routes(app, field_agent_graph, path="/field_agent")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
