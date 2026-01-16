# Python Rules

SCOPE: `src/backend/**/*.py`, `tests/backend/**/*.py`
TOOLS: Python 3.12+, uv, ruff, mypy

---

## Configuration

ALWAYS:

- Use `pydantic-settings` BaseSettings
- Use `env_nested_delimiter="__"` for nested
- Use `Field(description="...")` for all fields
- Use `SecretStr` for passwords/tokens
- Use singleton pattern: `get_settings()`

NEVER:

- `os.environ.get()` directly
- Hardcoded configuration values
- Mutable default values in Field()

PATTERN:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    """Main application settings with nested sub-settings."""

    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )
```

---

## Type Hints (Python 3.12+)

ALWAYS:

- Type all function parameters
- Type all return values (even None)
- Use `X | None` not `Optional[X]`
- Use `dict[K, V]` not `Dict[K, V]`
- Use `list[X]` not `List[X]`
- Use `from __future__ import annotations` for forward references

NEVER:

- Bare `Any` without comment
- `from typing import Optional, List, Dict`
- Old-style `Union[X, Y]` (use `X | Y`)

---

## Generics (PEP 695 - Python 3.12+)

ALWAYS:

- Use new syntax `class Foo[T]:` instead of `Generic[T]`
- Use new syntax `def foo[T](x: T) -> T:`
- Use bounded generics: `class Foo[T: BaseClass]:`

NEVER:

- `TypeVar("T")` declarations
- `from typing import Generic`

---

## Async/Await (Python 3.12+)

ALWAYS:

- Async for all I/O operations
- `asyncio.to_thread()` for blocking I/O in async context
- `httpx.AsyncClient` over `requests`
- `asynccontextmanager` for resource management

NEVER:

- `time.sleep()` in async (use `asyncio.sleep()`)
- `asyncio.get_event_loop()` (deprecated)
- Block event loop with sync I/O

---

## HTTP Client (httpx + tenacity)

ALWAYS:

- Use `httpx.AsyncClient` with connection pooling
- Use `tenacity` for retries with exponential backoff
- Set reasonable timeouts
- Handle rate limits gracefully

PATTERN:

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def fetch_usage(client: httpx.AsyncClient, token: str) -> dict:
    response = await client.get(
        "https://api.anthropic.com/api/oauth/usage",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

---

## Logging (loguru)

ALWAYS:

- Use `loguru` instead of stdlib logging
- Configure structured JSON logging for production
- Include context (user_id, request_id) via `bind()`
- Use appropriate log levels

PATTERN:

```python
from loguru import logger

logger.add("logs/app.log", rotation="10 MB", retention="7 days")

def process_request(request_id: str) -> None:
    log = logger.bind(request_id=request_id)
    log.info("Processing request")
```

---

## Pydantic Models (v2)

ALWAYS:

- Use `StrEnum` for JSON-safe enums
- Use `ConfigDict(use_enum_values=True)`
- Use `default_factory` for mutable defaults
- Include `description` in Field() for ALL fields
- Use `SecretStr` for sensitive data

PATTERN:

```python
from pydantic import BaseModel, ConfigDict, Field, SecretStr

class Credentials(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    access_token: SecretStr = Field(..., description="OAuth access token")
    expires_at: int | None = Field(None, description="Token expiration timestamp")
```

---

## Naming

```
Classes:      PascalCase       UsageTracker
Functions:    snake_case       fetch_usage()
Constants:    UPPER_SNAKE      CACHE_DURATION_MS
Private:      _underscore      _internal_method()
Modules:      kebab-case       usage-tracker.py
```
