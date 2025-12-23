"""Todo toolset for pydantic-ai agents.

Provides task planning and tracking capabilities for AI agents.
Compatible with any pydantic-ai agent - no specific deps required.

Example:
    ```python
    from pydantic_ai import Agent
    from pydantic_ai_todo import create_todo_toolset, TodoStorage

    # Simple usage
    agent = Agent("openai:gpt-4.1", toolsets=[create_todo_toolset()])

    # With storage access
    storage = TodoStorage()
    agent = Agent("openai:gpt-4.1", toolsets=[create_todo_toolset(storage)])
    result = await agent.run("Create 3 tasks")
    print(storage.todos)  # Access todos directly
    ```
"""

from pydantic_ai_todo.storage import TodoStorage, TodoStorageProtocol
from pydantic_ai_todo.toolset import (
    READ_TODO_DESCRIPTION,
    TODO_SYSTEM_PROMPT,
    TODO_TOOL_DESCRIPTION,
    create_todo_toolset,
    get_todo_system_prompt,
)
from pydantic_ai_todo.types import Todo, TodoItem

__all__ = [
    # Main factory
    "create_todo_toolset",
    "get_todo_system_prompt",
    # Types
    "Todo",
    "TodoItem",
    # Storage
    "TodoStorage",
    "TodoStorageProtocol",
    # Constants (for customization)
    "TODO_TOOL_DESCRIPTION",
    "TODO_SYSTEM_PROMPT",
    "READ_TODO_DESCRIPTION",
]

__version__ = "0.1.0"
