# CLAUDE.md

Guidance for Claude Code when working on this repository.

## What This Project Is

**pydantic-ai-todo** provides a todo/task planning toolset for pydantic-ai agents. It's designed to work standalone with any agent - no specific deps type required.

Key pattern: **Storage Injection** - tools use closure to capture state, not `ctx.deps`.

## Commands

```bash
uv sync --group dev          # Install dependencies
uv run pytest                # Run tests
uv run coverage run -m pytest && uv run coverage report  # Test with coverage
uv run ruff check .          # Lint
uv run ruff format .         # Format
uv run pyright               # Type check
```

## Structure

```
pydantic_ai_todo/
├── types.py      # Todo, TodoItem models
├── storage.py    # TodoStorage, TodoStorageProtocol
├── toolset.py    # create_todo_toolset(), get_todo_system_prompt()
└── __init__.py   # Public API exports
```

## Core Pattern

```python
def create_todo_toolset(storage=None) -> FunctionToolset[Any]:
    _storage = storage or TodoStorage()

    @toolset.tool
    async def read_todos() -> str:  # No ctx - uses closure
        return format(_storage.todos)
```

## Requirements

- **100% test coverage** - every PR must maintain this
- **Type annotations** - pyright strict mode
- **Async tools** - all tool functions are async

## Testing

```bash
# Run specific test
uv run pytest tests/test_toolset.py::TestCreateTodoToolset -v

# Debug mode
uv run pytest -v -s
```

## Integration

This library is used by [pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents) which re-exports its API. Changes here affect pydantic-deep users.
