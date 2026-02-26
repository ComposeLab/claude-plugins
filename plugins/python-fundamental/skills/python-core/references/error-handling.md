# Error Handling

Python uses exceptions as the primary mechanism for signaling and handling errors. The philosophy is that errors should be loud by default — silent failures lead to corrupted state that surfaces far from the original problem.

## try / except / else / finally

The full exception handling block has four clauses, each with a distinct purpose. `try` contains the code that might raise an exception. `except` catches specific exception types. `else` runs only if no exception was raised — use it to separate the "happy path" from error handling, which makes the scope of the try block minimal. `finally` runs unconditionally, making it the right place for cleanup.

```python
def read_config(path: str) -> dict:
    try:
        f = open(path)
    except FileNotFoundError:
        print(f"Config not found: {path}")
        return {}
    except PermissionError as e:
        print(f"Cannot read {path}: {e}")
        return {}
    else:
        # Only runs if open() succeeded
        import json
        data = json.load(f)
        f.close()
        return data
    finally:
        # Runs regardless — good for cleanup logging
        print(f"Config read attempt for {path} completed")
```

## Exception Hierarchy

All exceptions inherit from `BaseException`. User code should almost always catch subclasses of `Exception`, not `BaseException`. The distinction exists because `KeyboardInterrupt` and `SystemExit` inherit from `BaseException` directly — catching them accidentally prevents users from interrupting programs with Ctrl+C. A bare `except:` catches `BaseException`, which is why it should never be used.

```python
# The key hierarchy:
# BaseException
#   ├── SystemExit
#   ├── KeyboardInterrupt
#   ├── GeneratorExit
#   └── Exception
#       ├── ValueError
#       ├── TypeError
#       ├── KeyError
#       ├── IndexError
#       ├── FileNotFoundError
#       ├── RuntimeError
#       └── ... (hundreds more)

# WRONG — catches KeyboardInterrupt and SystemExit
try:
    do_something()
except:
    pass

# CORRECT — catches only Exception subclasses
try:
    do_something()
except Exception as e:
    log_error(e)
```

## Catching Multiple Exceptions

When different exception types need the same handling, group them in a tuple. When they need different handling, use separate except clauses ordered from most specific to least specific — Python matches the first applicable handler.

```python
# Same handling for multiple types
try:
    value = config[key]
except (KeyError, TypeError, IndexError):
    value = default

# Different handling — specific first
try:
    result = parse_and_compute(data)
except ValueError as e:
    print(f"Bad value: {e}")
except TypeError as e:
    print(f"Wrong type: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise  # Re-raise unexpected exceptions
```

## Re-raising and Exception Chaining

A bare `raise` in an except block re-raises the current exception with its original traceback. This is the correct way to log an error and still propagate it. Exception chaining with `raise ... from ...` links a new exception to an original cause, preserving the full error context for debugging.

```python
# Re-raising after logging
try:
    process(data)
except ValueError:
    logger.error("Invalid data encountered")
    raise  # Preserves original traceback

# Exception chaining
class ConfigError(Exception):
    pass

try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    raise ConfigError(f"Invalid config format") from e
# The traceback shows both exceptions and their relationship
```

## Custom Exception Classes

Define custom exceptions when your library or module needs to signal domain-specific errors that callers should be able to catch distinctly. Inherit from `Exception` (or a more specific built-in exception). Keep the hierarchy shallow — one or two base exceptions for your module is usually enough.

```python
class AppError(Exception):
    """Base exception for the application."""

class ValidationError(AppError):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""
    def __init__(self, resource: str, identifier: str) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' not found")

# Usage
def get_user(user_id: str) -> dict:
    user = db.find(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

## EAFP vs LBYL

EAFP (Easier to Ask Forgiveness than Permission) tries the operation and handles the exception. LBYL (Look Before You Leap) checks preconditions before acting. Python idiom favors EAFP because it avoids race conditions (the state could change between the check and the action) and is often more readable. LBYL is appropriate when the check is cheap and failure is the common case (to avoid exception overhead).

```python
# EAFP — Pythonic for most cases
try:
    value = mapping[key]
except KeyError:
    value = default

# LBYL — appropriate when misses are frequent
if key in mapping:
    value = mapping[key]
else:
    value = default

# EAFP with attribute access
try:
    result = obj.compute()
except AttributeError:
    result = fallback()
```

## Context Managers

The `with` statement ensures cleanup code runs even if an exception occurs. It calls `__enter__` on entry and `__exit__` on exit (including on exceptions). Context managers are the idiomatic way to manage resources: files, locks, database connections, temporary state changes.

```python
# File handling — always use with
with open("data.txt", "r") as f:
    content = f.read()
# f is automatically closed, even if an exception occurred

# Custom context manager using class protocol
class DatabaseConnection:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn = None

    def __enter__(self):
        self.conn = connect(self.dsn)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
        return False  # Do not suppress exceptions
```

## @contextmanager Decorator

For simple context managers, the `contextlib.contextmanager` decorator is more concise than writing a class with `__enter__` and `__exit__`. The code before `yield` runs on entry, the yielded value is the `as` target, and the code after `yield` runs on exit.

```python
from contextlib import contextmanager
import os

@contextmanager
def temporary_directory(path: str):
    """Create a directory, yield it, then clean up."""
    os.makedirs(path, exist_ok=True)
    try:
        yield path
    finally:
        import shutil
        shutil.rmtree(path)

with temporary_directory("/tmp/work") as d:
    # d is "/tmp/work" and exists
    process_files(d)
# Directory is removed after the block
```

## Warnings

The `warnings` module is for non-fatal conditions that users should know about but that should not interrupt execution — deprecation notices, potential performance issues, or suspicious but valid input. Unlike exceptions, warnings do not alter control flow by default.

```python
import warnings

def connect(host: str, use_ssl: bool = True) -> None:
    if not use_ssl:
        warnings.warn(
            "Connecting without SSL is insecure",
            UserWarning,
            stacklevel=2,
        )
    # proceed with connection...

# Callers can control warning behavior:
# warnings.filterwarnings("error")  # Turn warnings into exceptions
# warnings.filterwarnings("ignore") # Silence warnings
```
