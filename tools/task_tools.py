
# Create the ADK Tools for Task Management

import json
from pathlib import Path
from typing import Any, Dict, List

TASKS_PATH = Path("tasks.json")


def load_tasks() -> List[Dict[str, Any]]:
    """
    Load tasks from tasks.json.
    Returns a list of tasks; each task is a dict:
    {
      "id": int,
      "description": str,
      "done": bool
    }
    """
    if not TASKS_PATH.exists():
        return []

    try:
        with TASKS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    """
    Save tasks list back to tasks.json.
    """
    with TASKS_PATH.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
