
# Create TaskManagerAgent
# agents/task_manager.py
# agents/task_manager.py

import os, json
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


class TaskManagerAgent(LlmAgent):

    def __init__(self):
        super().__init__(
            name="task_manager",
            description="Manages to-do tasks. Returns JSON only.",
            model=Gemini(
                model_name="gemini-2.5-flash-lite",
                api_key=os.environ.get("GOOGLE_API_KEY"),
            ),
            tools=[
                FunctionTool(self.add_task),
                FunctionTool(self.list_tasks),
                FunctionTool(self.delete_task),
            ]
        )

    async def add_task(self, title: str, details: str = ""):
        """Add a new task to the task list."""
        tasks = load_tasks()
        tasks.append({"title": title, "details": details})
        save_tasks(tasks)
        return {"status": "ok", "tasks": tasks}

    async def list_tasks(self):
        """Return all tasks."""
        return {"status": "ok", "tasks": load_tasks()}

    async def delete_task(self, index: int):
        """Delete a task by index."""
        tasks = load_tasks()
        if 0 <= index < len(tasks):
            removed = tasks.pop(index)
            save_tasks(tasks)
            return {"status": "ok", "removed": removed, "tasks": tasks}
        return {"status": "error", "message": "index out of range"}
