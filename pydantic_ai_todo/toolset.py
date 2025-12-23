"""Todo toolset for pydantic-ai agents."""

from __future__ import annotations

from typing import Any

from pydantic_ai.toolsets import FunctionToolset

from pydantic_ai_todo.storage import TodoStorage, TodoStorageProtocol
from pydantic_ai_todo.types import Todo, TodoItem

TODO_TOOL_DESCRIPTION = """
Use this tool to create and manage a structured task list for your current session.
This helps you track progress, organize complex tasks, and demonstrate thoroughness.

## When to Use This Tool
Use this tool in these scenarios:
1. Complex multi-step tasks - When a task requires 3 or more distinct steps
2. Non-trivial tasks - Tasks that require careful planning
3. User provides multiple tasks - When users provide a list of things to be done
4. After receiving new instructions - Capture user requirements as todos
5. When starting a task - Mark it as in_progress BEFORE beginning work
6. After completing a task - Mark it as completed immediately

## Task States
- pending: Task not yet started
- in_progress: Currently working on (limit to ONE at a time)
- completed: Task finished successfully

## Important
- Exactly ONE task should be in_progress at any time
- Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
- If you encounter blockers, keep the task as in_progress and create a new task for the blocker
"""

TODO_SYSTEM_PROMPT = """
## Task Management

You have access to the `write_todos` tool to track your tasks.
Use it frequently to:
- Plan complex tasks before starting
- Show progress to the user
- Keep track of what's done and what's pending

When working on tasks:
1. Break down complex tasks into smaller steps
2. Mark exactly one task as in_progress at a time
3. Mark tasks as completed immediately after finishing
"""

READ_TODO_DESCRIPTION = """
Read the current todo list state.

Use this tool to check the current status of all tasks before:
- Deciding what to work on next
- Updating task statuses
- Reporting progress to the user

Returns all todos with their current status (pending, in_progress, completed).
"""


def create_todo_toolset(
    storage: TodoStorageProtocol | None = None,
    *,
    id: str | None = None,
) -> FunctionToolset[Any]:
    """Create a todo toolset for task management.

    This toolset provides read_todos and write_todos tools for AI agents
    to track and manage tasks during a session.

    Args:
        storage: Optional storage backend. Defaults to in-memory TodoStorage.
            You can provide a custom storage implementing TodoStorageProtocol
            for persistence or integration with other systems.
        id: Optional unique ID for the toolset.

    Returns:
        FunctionToolset compatible with any pydantic-ai agent.

    Example (standalone):
        ```python
        from pydantic_ai import Agent
        from pydantic_ai_todo import create_todo_toolset

        agent = Agent("openai:gpt-4.1", toolsets=[create_todo_toolset()])
        result = await agent.run("Create a todo list for my project")
        ```

    Example (with custom storage):
        ```python
        from pydantic_ai_todo import create_todo_toolset, TodoStorage

        storage = TodoStorage()
        toolset = create_todo_toolset(storage=storage)

        # After agent runs, access todos directly
        print(storage.todos)
        ```
    """
    _storage = storage if storage is not None else TodoStorage()

    toolset: FunctionToolset[Any] = FunctionToolset(id=id)

    @toolset.tool(description=READ_TODO_DESCRIPTION)
    async def read_todos() -> str:
        """Read the current todo list."""
        if not _storage.todos:
            return "No todos in the list. Use write_todos to create tasks."

        lines = ["Current todos:"]
        for i, todo in enumerate(_storage.todos, 1):
            status_icon = {
                "pending": "[ ]",
                "in_progress": "[*]",
                "completed": "[x]",
            }.get(todo.status, "[ ]")
            lines.append(f"{i}. {status_icon} {todo.content}")

        # Add summary
        counts = {"pending": 0, "in_progress": 0, "completed": 0}
        for todo in _storage.todos:
            counts[todo.status] += 1

        lines.append("")
        lines.append(
            f"Summary: {counts['completed']} completed, "
            f"{counts['in_progress']} in progress, "
            f"{counts['pending']} pending"
        )

        return "\n".join(lines)

    @toolset.tool(description=TODO_TOOL_DESCRIPTION)
    async def write_todos(todos: list[TodoItem]) -> str:
        """Update the todo list with new items.

        Args:
            todos: List of todo items with content, status, and active_form.
        """
        _storage.todos = [
            Todo(content=t.content, status=t.status, active_form=t.active_form) for t in todos
        ]

        # Count by status
        counts = {"pending": 0, "in_progress": 0, "completed": 0}
        for todo in _storage.todos:
            counts[todo.status] += 1

        return (
            f"Updated {len(todos)} todos: "
            f"{counts['completed']} completed, "
            f"{counts['in_progress']} in progress, "
            f"{counts['pending']} pending"
        )

    return toolset


def get_todo_system_prompt(storage: TodoStorageProtocol | None = None) -> str:
    """Generate dynamic system prompt section for todos.

    Args:
        storage: Optional storage to read current todos from.

    Returns:
        System prompt section with current todos, or base prompt if no todos.
    """
    if storage is None or not storage.todos:
        return TODO_SYSTEM_PROMPT

    lines = [TODO_SYSTEM_PROMPT, "", "## Current Todos"]

    for todo in storage.todos:
        status_icon = {
            "pending": "[ ]",
            "in_progress": "[*]",
            "completed": "[x]",
        }.get(todo.status, "[ ]")
        lines.append(f"- {status_icon} {todo.content}")

    return "\n".join(lines)
