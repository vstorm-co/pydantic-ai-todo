"""Type definitions for pydantic-ai-todo."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Todo(BaseModel):
    """A todo item for task tracking.

    Attributes:
        content: The task description in imperative form (e.g., 'Implement feature X').
        status: Task status - 'pending', 'in_progress', or 'completed'.
        active_form: Present continuous form shown during execution
            (e.g., 'Implementing feature X').
    """

    content: str
    status: Literal["pending", "in_progress", "completed"]
    active_form: str


class TodoItem(BaseModel):
    """Input model for the write_todos tool.

    This is the model that agents use when calling write_todos.
    It has the same fields as Todo but with Field descriptions for LLM guidance.
    """

    content: str = Field(
        ..., description="The task description in imperative form (e.g., 'Implement feature X')"
    )
    status: Literal["pending", "in_progress", "completed"] = Field(
        ..., description="Task status: pending, in_progress, or completed"
    )
    active_form: str = Field(
        ...,
        description="Present continuous form during execution (e.g., 'Implementing feature X')",
    )
