"""
manual_a2a_agent.py
--------------------
A guaranteed-working manual A2A server for ConciergeX
using InMemoryRunner (compatible with your google-adk version).

Provides:
- GET  /.well-known/agent.json  → A2A Agent Card
- POST /execute                 → A2A Execution Endpoint
"""

import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# ADK Imports (your current ADK version supports InMemoryRunner only)
from google.adk.runners import InMemoryRunner
from agents.orchestrator import OrchestratorAgent


# ---------------------------------------------------------
# Load environment variables (MUST COME BEFORE agent init)
# ---------------------------------------------------------
load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY not found. Add it to .env.")


# ---------------------------------------------------------
# Initialize ConciergeX Root Agent
# ---------------------------------------------------------
agent = OrchestratorAgent()

runner = InMemoryRunner(
    agent=agent,
    app_name="agents"
)


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------
app = FastAPI(
    title="ConciergeX A2A Agent",
    version="1.0",
    description="Manual A2A wrapper around ConciergeX OrchestratorAgent"
)


# Input model for A2A requests
class A2ARequest(BaseModel):
    input: str


# ---------------------------------------------------------
# A2A AGENT CARD ENDPOINT
# ---------------------------------------------------------
@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "ConciergeX A2A Agent",
        "description": "Manual A2A wrapper around OrchestratorAgent",
        "version": "1.0",
        "endpoints": ["/execute"],
        "input_modes": ["text"],
        "output_modes": ["json"]
    }


# ---------------------------------------------------------
# EXECUTION ENDPOINT — CLEAN JSON OUTPUT
# ---------------------------------------------------------
@app.post("/execute")
async def execute(req: A2ARequest):
    # Run pipeline via ADK
    events = await runner.run_debug(req.input)

    # Extract usable text from last event
    raw_text = None
    try:
        parts = events[-1].content.parts
        for p in parts:
            if hasattr(p, "text") and p.text:
                raw_text = p.text.strip()
                break
    except:
        pass

    if not raw_text:
        return {"output": "No textual response found."}

    # -------------------------------
    # CLEAN OUTPUT FOR STREAMLIT
    # Remove markdown fences like:
    # ```json
    # { ... }
    # ```
    # -------------------------------
    cleaned = raw_text

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()

        # Remove leading "json"
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    # remove any remaining triple-backticks
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    return {"output": cleaned}


# ---------------------------------------------------------
# LOCAL RUN ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Manual A2A server running at http://localhost:8001")
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent.json")
    print("⚡ Execute via: POST http://localhost:8001/execute")
    uvicorn.run(app, host="0.0.0.0", port=8001)

