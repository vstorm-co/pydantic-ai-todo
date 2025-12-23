"""Tests for pydantic_ai_todo.types module."""

import pytest
from pydantic import ValidationError

from pydantic_ai_todo import Todo, TodoItem


class TestTodo:
    """Tests for Todo model."""

    def test_create_todo(self) -> None:
        """Test creating a valid todo."""
        todo = Todo(
            content="Implement feature X",
            status="pending",
            active_form="Implementing feature X",
        )
        assert todo.content == "Implement feature X"
        assert todo.status == "pending"
        assert todo.active_form == "Implementing feature X"

    def test_todo_status_values(self) -> None:
        """Test all valid status values."""
        for status in ["pending", "in_progress", "completed"]:
            todo = Todo(content="Task", status=status, active_form="Working")  # type: ignore[arg-type]
            assert todo.status == status

    def test_todo_invalid_status(self) -> None:
        """Test that invalid status raises validation error."""
        with pytest.raises(ValidationError):
            Todo(content="Task", status="invalid", active_form="Working")  # type: ignore[arg-type]

    def test_todo_model_dump(self) -> None:
        """Test serialization to dict."""
        todo = Todo(
            content="Task",
            status="in_progress",
            active_form="Working",
        )
        data = todo.model_dump()
        assert data == {
            "content": "Task",
            "status": "in_progress",
            "active_form": "Working",
        }


class TestTodoItem:
    """Tests for TodoItem model."""

    def test_create_todo_item(self) -> None:
        """Test creating a valid todo item."""
        item = TodoItem(
            content="Implement feature X",
            status="pending",
            active_form="Implementing feature X",
        )
        assert item.content == "Implement feature X"
        assert item.status == "pending"
        assert item.active_form == "Implementing feature X"

    def test_todo_item_field_descriptions(self) -> None:
        """Test that fields have descriptions for LLM guidance."""
        schema = TodoItem.model_json_schema()
        props = schema["properties"]

        assert "description" in props["content"]
        assert "description" in props["status"]
        assert "description" in props["active_form"]

    def test_todo_item_invalid_status(self) -> None:
        """Test that invalid status raises validation error."""
        with pytest.raises(ValidationError):
            TodoItem(content="Task", status="invalid", active_form="Working")  # type: ignore[arg-type]
