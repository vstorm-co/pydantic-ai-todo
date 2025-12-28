# pydantic-ai-todo

> **Looking for a complete agent framework?** Check out [pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents) - a full-featured deep agent framework with planning, subagents, and skills system built on pydantic-ai.

> **Need file storage or Docker sandbox?** Check out [pydantic-ai-backend](https://github.com/vstorm-co/pydantic-ai-backend) - file storage and sandbox backends that work with any pydantic-ai agent.

> **Want a full-stack template?** Check out [fastapi-fullstack](https://github.com/vstorm-co/full-stack-fastapi-nextjs-llm-template) - production-ready AI/LLM application template with FastAPI, Next.js, and pydantic-deep integration.

[![PyPI version](https://img.shields.io/pypi/v/pydantic-ai-todo.svg)](https://pypi.org/project/pydantic-ai-todo/)
[![CI](https://github.com/vstorm-co/pydantic-ai-todo/actions/workflows/ci.yml/badge.svg)](https://github.com/vstorm-co/pydantic-ai-todo/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/vstorm-co/pydantic-ai-todo)
[![Python](https://img.shields.io/pypi/pyversions/pydantic-ai-todo.svg)](https://pypi.org/project/pydantic-ai-todo/)
[![License](https://img.shields.io/github/license/vstorm-co/pydantic-ai-todo)](https://github.com/vstorm-co/pydantic-ai-todo/blob/main/LICENSE)

Todo/task planning toolset for [pydantic-ai](https://ai.pydantic.dev/) agents.

**This library was extracted from [pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents)** to provide standalone task planning for any pydantic-ai agent without requiring the full framework.

Provides `read_todos` and `write_todos` tools that help AI agents track and manage tasks during a session.

## Installation

```bash
pip install pydantic-ai-todo
```

Or with uv:

```bash
uv add pydantic-ai-todo
```

## Quick Start

```python
from pydantic_ai import Agent
from pydantic_ai_todo import create_todo_toolset

# Create an agent with todo capabilities
agent = Agent(
    "openai:gpt-4.1",
    toolsets=[create_todo_toolset()],
)

# Run the agent
result = await agent.run("Create a todo list for building a website")
```

## Usage with Storage Access

If you need to access the todos after the agent runs:

```python
from pydantic_ai import Agent
from pydantic_ai_todo import create_todo_toolset, TodoStorage

# Create storage and toolset
storage = TodoStorage()
toolset = create_todo_toolset(storage=storage)

agent = Agent("openai:gpt-4.1", toolsets=[toolset])

# Run the agent
result = await agent.run("Plan the implementation of a REST API")

# Access todos directly
for todo in storage.todos:
    print(f"[{todo.status}] {todo.content}")
```

## Custom Storage

You can implement custom storage (e.g., for persistence):

```python
import json
from pydantic_ai_todo import create_todo_toolset, TodoStorageProtocol, Todo

class RedisTodoStorage:
    """Store todos in Redis."""

    def __init__(self, redis_client):
        self._redis = redis_client

    @property
    def todos(self) -> list[Todo]:
        data = self._redis.get("todos")
        if not data:
            return []
        return [Todo(**t) for t in json.loads(data)]

    @todos.setter
    def todos(self, value: list[Todo]) -> None:
        self._redis.set("todos", json.dumps([t.model_dump() for t in value]))

# Use with agent
storage = RedisTodoStorage(redis.Redis())
agent = Agent("openai:gpt-4.1", toolsets=[create_todo_toolset(storage)])
```

## System Prompt Integration

Include current todos in the system prompt:

```python
from pydantic_ai_todo import get_todo_system_prompt, TodoStorage

storage = TodoStorage()
# ... agent populates todos ...

# Generate system prompt section with current todos
prompt_section = get_todo_system_prompt(storage)
```

## API Reference

### `create_todo_toolset(storage=None, *, id=None)`

Creates a todo toolset with `read_todos` and `write_todos` tools.

**Parameters:**
- `storage`: Optional `TodoStorageProtocol` implementation. Defaults to in-memory `TodoStorage`.
- `id`: Optional unique ID for the toolset.

**Returns:** `FunctionToolset[Any]`

### `get_todo_system_prompt(storage=None)`

Generates a system prompt section for task management.

**Parameters:**
- `storage`: Optional storage to read current todos from.

**Returns:** `str` - System prompt with optional current todos section.

### `Todo`

Pydantic model for a todo item.

```python
class Todo(BaseModel):
    content: str  # Task description in imperative form
    status: Literal["pending", "in_progress", "completed"]
    active_form: str  # Present continuous form (e.g., "Implementing...")
```

### `TodoStorage`

Default in-memory storage implementation.

```python
storage = TodoStorage()
storage.todos = [Todo(...), Todo(...)]
print(storage.todos)
```

### `TodoStorageProtocol`

Protocol for custom storage implementations. Must have a `todos` property with getter and setter.

## Related Projects

- **[pydantic-ai](https://github.com/pydantic/pydantic-ai)** - The foundation: Agent framework by Pydantic
- **[pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents)** - Full agent framework (uses this library)
- **[pydantic-ai-backend](https://github.com/vstorm-co/pydantic-ai-backend)** - File storage and sandbox backends
- **[fastapi-fullstack](https://github.com/vstorm-co/full-stack-fastapi-nextjs-llm-template)** - Full-stack AI app template

## License

[MIT](LICENSE)
