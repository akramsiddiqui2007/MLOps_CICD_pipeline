"""
local_a2a_agent.py
------------------

This script exposes your existing ConciergeX OrchestratorAgent as a fully
A2A-compliant LOCAL agent, without modifying your internal agent architecture.

Endpoints provided:
- GET /.well-known/agent.json   (A2A Agent Card)
- POST /a2a/execute             (Main A2A execution endpoint)
- GET /health                   (Health check)

Run:
    uvicorn local_a2a_agent:app --host 0.0.0.0 --port 8001
"""

import os
from dotenv import load_dotenv
import uvicorn

from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Import your existing ConciergeX orchestrator (NO CHANGES REQUIRED)
from agents.orchestrator import OrchestratorAgent


# ----------------------------------------------------------------------
# 1. Load environment variables (GOOGLE_API_KEY, etc.)
# ----------------------------------------------------------------------
load_dotenv()


# ----------------------------------------------------------------------
# 2. Create your existing root agent exactly as-is
# ----------------------------------------------------------------------
root_agent = OrchestratorAgent()


# ----------------------------------------------------------------------
# 3. Wrap it into an A2A-compliant FastAPI app
# ----------------------------------------------------------------------
app = to_a2a(root_agent)
# This automatically creates:
# - /.well-known/agent.json
# - /a2a/execute
# - /health


# ----------------------------------------------------------------------
# 4. Run locally (optional, useful for dev)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Local A2A ConciergeX Agent at http://localhost:8001")
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent.json")
    print("⚡ Execute via: POST http://localhost:8001/a2a/execute")
    uvicorn.run(app, host="0.0.0.0", port=8001)

