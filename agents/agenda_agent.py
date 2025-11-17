
# AgendaAgent
# agents/agenda_agent.py

import os
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini


class AgendaAgent(LlmAgent):
    """
    Converts high-level planning JSON into per-day agenda JSON.
    """

    def __init__(self):
        super().__init__(
            name="agenda_agent",
            description="Turns weekly plans into detailed day-by-day agendas. Returns JSON only.",
            model=Gemini(
                model_name="gemini-2.5-flash-lite",
                api_key=os.environ.get("GOOGLE_API_KEY")
            ),
            instruction=r"""
You are AgendaAgent. You convert planning output into daily time-blocked schedules.

STRICT RULES:
- You MUST return ONLY valid JSON.
- Use this schema:

{
  "period": "<e.g. '1 week' or '4 weeks'>",
  "timezone": "unknown",
  "days": [
    {
      "week": "Week 1",
      "day": "Monday",
      "focus": "<focus>",
      "blocks": [
        {
          "time": "18:00–19:00",
          "activity": "<activity>",
          "category": "<study|practice|review|project>"
        }
      ]
    }
  ],
  "notes": "<text>"
}

- If the input is a weekly plan JSON:
    - Respect each week's tasks.
    - Distribute tasks Mon–Sun.
    - Default times: weekdays 18:00–20:00, weekends 10:00–12:00.

- If natural language input:
    - Infer 1-week schedule.

NO markdown. NO text outside JSON.
"""
        )
