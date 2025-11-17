
# Create PlanningAgent
# agents/planning_agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini


class PlanningAgent(LlmAgent):
    """
    Produces high-level weekly/monthly plans.
    MUST return JSON only.
    """

    def __init__(self):
        super().__init__(
            name="planning_agent",
            description="Creates structured multi-week learning plans. Returns JSON only.",
            model=Gemini(
                model_name="gemini-2.5-flash-lite",
                api_key=os.environ.get("GOOGLE_API_KEY")
            ),
            instruction=r"""
You are PlanningAgent. You create high-level structured learning plans.

STRICT RULES:
- Output ONLY valid JSON. No markdown. No backticks.
- JSON MUST follow this schema exactly:

{
  "goal": "<goal text>",
  "duration": "<e.g. '4 weeks'>",
  "weeks": [
    {
      "week": "Week 1",
      "focus": "<theme>",
      "tasks": [
        "<task 1>",
        "<task 2>"
      ]
    }
  ],
  "notes": "<extra notes>"
}

If user gives natural text, infer goal + duration + weekly breakdown.

Never include explanations outside JSON.
"""
        )
