"""Tests for pydantic_ai_todo.toolset module."""

from typing import Any

import pytest
from pydantic_ai.toolsets import FunctionToolset

from pydantic_ai_todo import (
    Todo,
    TodoItem,
    TodoStorage,
    create_todo_toolset,
    get_todo_system_prompt,
)


class TestCreateTodoToolset:
    """Tests for create_todo_toolset factory."""

    def test_returns_function_toolset(self) -> None:
        """Test that factory returns a FunctionToolset."""
        toolset = create_todo_toolset()
        assert isinstance(toolset, FunctionToolset)

    def test_toolset_has_read_todos_tool(self) -> None:
        """Test that toolset has read_todos tool."""
        toolset = create_todo_toolset()
        assert "read_todos" in toolset.tools

    def test_toolset_has_write_todos_tool(self) -> None:
        """Test that toolset has write_todos tool."""
        toolset = create_todo_toolset()
        assert "write_todos" in toolset.tools

    def test_toolset_with_custom_id(self) -> None:
        """Test creating toolset with custom ID."""
        toolset = create_todo_toolset(id="my-todos")
        assert toolset.id == "my-todos"

    def test_toolset_with_custom_storage(self) -> None:
        """Test creating toolset with custom storage."""
        storage = TodoStorage()
        toolset = create_todo_toolset(storage=storage)
        assert toolset is not None

    def test_default_storage_isolation(self) -> None:
        """Test that each toolset has isolated storage by default."""
        toolset1 = create_todo_toolset()
        toolset2 = create_todo_toolset()
        # They should be different instances
        assert toolset1 is not toolset2


class TestReadTodos:
    """Tests for read_todos tool."""

    @pytest.fixture
    def storage(self) -> TodoStorage:
        """Create a storage instance."""
        return TodoStorage()

    @pytest.fixture
    def toolset(self, storage: TodoStorage) -> FunctionToolset[Any]:
        """Create a toolset with the storage."""
        return create_todo_toolset(storage=storage)

    async def test_read_empty_todos(self, toolset: FunctionToolset[Any]) -> None:
        """Test reading when no todos exist."""
        read_todos = toolset.tools["read_todos"]
        result = await read_todos.function()  # type: ignore[call-arg]
        assert "No todos" in result

    async def test_read_todos_with_items(
        self, storage: TodoStorage, toolset: FunctionToolset[Any]
    ) -> None:
        """Test reading todos with items."""
        storage.todos = [
            Todo(content="Task 1", status="pending", active_form="Working on Task 1"),
            Todo(content="Task 2", status="in_progress", active_form="Working on Task 2"),
            Todo(content="Task 3", status="completed", active_form="Working on Task 3"),
        ]

        read_todos = toolset.tools["read_todos"]
        result = await read_todos.function()  # type: ignore[call-arg]

        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" in result
        assert "[ ]" in result  # pending icon
        assert "[*]" in result  # in_progress icon
        assert "[x]" in result  # completed icon

    async def test_read_todos_summary(
        self, storage: TodoStorage, toolset: FunctionToolset[Any]
    ) -> None:
        """Test that read_todos includes summary."""
        storage.todos = [
            Todo(content="Task 1", status="pending", active_form="Working"),
            Todo(content="Task 2", status="pending", active_form="Working"),
            Todo(content="Task 3", status="completed", active_form="Working"),
        ]

        read_todos = toolset.tools["read_todos"]
        result = await read_todos.function()  # type: ignore[call-arg]

        assert "1 completed" in result
        assert "2 pending" in result


class TestWriteTodos:
    """Tests for write_todos tool."""

    @pytest.fixture
    def storage(self) -> TodoStorage:
        """Create a storage instance."""
        return TodoStorage()

    @pytest.fixture
    def toolset(self, storage: TodoStorage) -> FunctionToolset[Any]:
        """Create a toolset with the storage."""
        return create_todo_toolset(storage=storage)

    async def test_write_todos(self, storage: TodoStorage, toolset: FunctionToolset[Any]) -> None:
        """Test writing todos."""
        write_todos = toolset.tools["write_todos"]

        items = [
            TodoItem(content="Task 1", status="pending", active_form="Working on Task 1"),
            TodoItem(content="Task 2", status="in_progress", active_form="Working on Task 2"),
        ]

        result = await write_todos.function(todos=items)  # type: ignore[call-arg]

        assert len(storage.todos) == 2
        assert storage.todos[0].content == "Task 1"
        assert storage.todos[1].status == "in_progress"
        assert "Updated 2 todos" in result

    async def test_write_todos_overwrites(
        self, storage: TodoStorage, toolset: FunctionToolset[Any]
    ) -> None:
        """Test that write_todos overwrites existing todos."""
        storage.todos = [
            Todo(content="Old task", status="pending", active_form="Working"),
        ]

        write_todos = toolset.tools["write_todos"]
        items = [
            TodoItem(content="New task", status="completed", active_form="Working"),
        ]
        await write_todos.function(todos=items)  # type: ignore[call-arg]

        assert len(storage.todos) == 1
        assert storage.todos[0].content == "New task"

    async def test_write_todos_returns_summary(
        self, storage: TodoStorage, toolset: FunctionToolset[Any]
    ) -> None:
        """Test that write_todos returns status summary."""
        write_todos = toolset.tools["write_todos"]
        items = [
            TodoItem(content="Task 1", status="pending", active_form="Working"),
            TodoItem(content="Task 2", status="in_progress", active_form="Working"),
            TodoItem(content="Task 3", status="completed", active_form="Working"),
        ]
        result = await write_todos.function(todos=items)  # type: ignore[call-arg]

        assert "3 todos" in result
        assert "1 completed" in result
        assert "1 in progress" in result
        assert "1 pending" in result


class TestGetTodoSystemPrompt:
    """Tests for get_todo_system_prompt function."""

    def test_prompt_without_storage(self) -> None:
        """Test system prompt without storage."""
        prompt = get_todo_system_prompt()
        assert "Task Management" in prompt
        assert "write_todos" in prompt

    def test_prompt_with_empty_storage(self) -> None:
        """Test system prompt with empty storage."""
        storage = TodoStorage()
        prompt = get_todo_system_prompt(storage)
        assert "Task Management" in prompt
        # Should not include "Current Todos" section
        assert "Current Todos" not in prompt

    def test_prompt_with_todos(self) -> None:
        """Test system prompt includes current todos."""
        storage = TodoStorage()
        storage.todos = [
            Todo(content="Task 1", status="pending", active_form="Working"),
            Todo(content="Task 2", status="in_progress", active_form="Working"),
        ]

        prompt = get_todo_system_prompt(storage)

        assert "Current Todos" in prompt
        assert "Task 1" in prompt
        assert "Task 2" in prompt
        assert "[ ]" in prompt  # pending
        assert "[*]" in prompt  # in_progress

    def test_prompt_todos_status_icons(self) -> None:
        """Test that prompt shows correct status icons."""
        storage = TodoStorage()
        storage.todos = [
            Todo(content="Pending", status="pending", active_form="Working"),
            Todo(content="In Progress", status="in_progress", active_form="Working"),
            Todo(content="Completed", status="completed", active_form="Working"),
        ]

        prompt = get_todo_system_prompt(storage)

        assert "[ ] Pending" in prompt
        assert "[*] In Progress" in prompt
        assert "[x] Completed" in prompt
