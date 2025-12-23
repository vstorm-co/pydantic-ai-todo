"""Storage abstraction for todo items."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from pydantic_ai_todo.types import Todo


@runtime_checkable
class TodoStorageProtocol(Protocol):
    """Protocol for todo storage implementations.

    Any class that has a `todos` property (read/write) implementing
    `list[Todo]` can be used as storage for the todo toolset.

    Example:
        ```python
        class MyCustomStorage:
            def __init__(self):
                self._todos: list[Todo] = []

            @property
            def todos(self) -> list[Todo]:
                return self._todos

            @todos.setter
            def todos(self, value: list[Todo]) -> None:
                self._todos = value
        ```
    """

    @property
    def todos(self) -> list[Todo]:
        """Get the current list of todos."""
        ...

    @todos.setter
    def todos(self, value: list[Todo]) -> None:
        """Set the list of todos."""
        ...


@dataclass
class TodoStorage:
    """Default in-memory todo storage.

    Simple implementation that stores todos in memory.
    Use this for standalone agents or testing.

    Example:
        ```python
        from pydantic_ai_todo import create_todo_toolset, TodoStorage

        storage = TodoStorage()
        toolset = create_todo_toolset(storage=storage)

        # After agent runs, access todos directly
        print(storage.todos)
        ```
    """

    _todos: list[Todo] = field(default_factory=lambda: [])

    @property
    def todos(self) -> list[Todo]:
        """Get the current list of todos."""
        return self._todos

    @todos.setter
    def todos(self, value: list[Todo]) -> None:
        """Set the list of todos."""
        self._todos = value
