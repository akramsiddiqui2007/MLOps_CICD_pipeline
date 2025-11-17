
# Create the ADK Tools for Task Management

# agents/task_tools.py
# agents/task_tools.py

import json
import os
from google.adk.tools import AgentTool
from agents.task_manager import TaskManagerAgent


class TaskTool(AgentTool):
    """
    ADK-Compatible Task Tool

    - Wraps TaskManagerAgent backend
    - Implements a single tool interface for orchestrator
    - Exposes: action = ["add", "list", "delete"]
    """

    def __init__(self):
        # Required attributes BEFORE calling super()
        self.name = "task_manager"
        self.description = "Manage user tasks (add, list, delete)."

        # Backend task manager
        self.manager = TaskManagerAgent()

        # Initialize as a tool
        super().__init__(agent=self)

    async def run(self, action: str, title: str = "", task_id: int = 0):
        """
        Executes task operations based on the tool call.
        Always returns JSON-serializable dict.
        """

        if action == "list":
            tasks = await self.manager.list_tasks()
            return {"status": "ok", "tasks": tasks}

        if action == "add":
            result = await self.manager.add_task(title)
            return {"status": "ok", "added": result}

        if action == "delete":
            result = await self.manager.delete_task(task_id)
            return {"status": "ok", "deleted": result}

        return {"status": "error", "message": f"Unknown action '{action}'"}
