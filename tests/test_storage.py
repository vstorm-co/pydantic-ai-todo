"""Tests for pydantic_ai_todo.storage module."""

from pydantic_ai_todo import Todo, TodoStorage, TodoStorageProtocol


class TestTodoStorage:
    """Tests for TodoStorage."""

    def test_default_empty(self) -> None:
        """Test that storage is empty by default."""
        storage = TodoStorage()
        assert storage.todos == []

    def test_set_and_get_todos(self) -> None:
        """Test setting and getting todos."""
        storage = TodoStorage()
        todos = [
            Todo(content="Task 1", status="pending", active_form="Working on Task 1"),
            Todo(content="Task 2", status="completed", active_form="Working on Task 2"),
        ]
        storage.todos = todos
        assert storage.todos == todos
        assert len(storage.todos) == 2

    def test_overwrite_todos(self) -> None:
        """Test that setting todos overwrites previous list."""
        storage = TodoStorage()
        storage.todos = [
            Todo(content="Task 1", status="pending", active_form="Working"),
        ]
        storage.todos = [
            Todo(content="Task 2", status="completed", active_form="Working"),
        ]
        assert len(storage.todos) == 1
        assert storage.todos[0].content == "Task 2"

    def test_clear_todos(self) -> None:
        """Test clearing todos by setting empty list."""
        storage = TodoStorage()
        storage.todos = [
            Todo(content="Task", status="pending", active_form="Working"),
        ]
        storage.todos = []
        assert storage.todos == []


class TestTodoStorageProtocol:
    """Tests for TodoStorageProtocol."""

    def test_todo_storage_implements_protocol(self) -> None:
        """Test that TodoStorage implements TodoStorageProtocol."""
        storage = TodoStorage()
        assert isinstance(storage, TodoStorageProtocol)

    def test_custom_storage_can_implement_protocol(self) -> None:
        """Test that custom storage can implement the protocol."""

        class CustomStorage:
            def __init__(self) -> None:
                self._data: list[Todo] = []

            @property
            def todos(self) -> list[Todo]:
                return self._data

            @todos.setter
            def todos(self, value: list[Todo]) -> None:
                self._data = value

        storage = CustomStorage()
        assert isinstance(storage, TodoStorageProtocol)

        # Test it works
        storage.todos = [
            Todo(content="Test", status="pending", active_form="Testing"),
        ]
        assert len(storage.todos) == 1
