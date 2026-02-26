# Functions and Decorators

Functions are first-class objects in Python, meaning they can be assigned to variables, passed as arguments, and returned from other functions. This property is the foundation for closures, higher-order functions, and the decorator pattern.

## Function Basics

Python functions are defined with `def` and can return any object. If no return statement is reached, the function implicitly returns `None`. Functions support multiple return values via tuple packing, which callers unpack naturally.

```python
def divide(a: float, b: float) -> tuple[float, bool]:
    """Divide a by b, returning (result, success)."""
    if b == 0:
        return 0.0, False
    return a / b, True

result, ok = divide(10, 3)
```

## Parameter Patterns

Python offers flexible parameter handling. Positional-only parameters (before `/`) prevent callers from using keyword syntax, which is useful for APIs where parameter names are implementation details. Keyword-only parameters (after `*`) force callers to be explicit, improving readability at call sites. The `*args` and `**kwargs` patterns collect variable positional and keyword arguments respectively, enabling delegation and wrapper functions.

```python
# Positional-only (/) and keyword-only (*) parameters
def query(sql: str, /, *, timeout: int = 30) -> list:
    """sql is positional-only; timeout is keyword-only."""
    ...

query("SELECT 1", timeout=10)  # OK
# query(sql="SELECT 1")        # TypeError — sql is positional-only

# *args and **kwargs for flexible signatures
def log(message: str, *tags: str, **metadata: str) -> None:
    print(f"[{', '.join(tags)}] {message}", metadata)

log("started", "info", "system", user="admin")
```

## Default Arguments

Default argument values are evaluated once at function definition time, not at each call. This means mutable defaults (lists, dicts) are shared across all invocations — a common source of bugs. The standard pattern is to use `None` as the default and create the mutable object inside the function body.

```python
# Correct pattern for mutable defaults
def process(items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append("processed")
    return items
```

## First-Class Functions and Closures

Because functions are objects, you can store them in data structures, pass them to other functions, and return them from functions. A closure is a function that captures variables from its enclosing scope. Closures are how decorators work internally — the wrapper function closes over the original function.

```python
# Functions as arguments
def apply(func, value):
    return func(value)

apply(str.upper, "hello")  # "HELLO"

# Closure — inner function captures outer variable
def make_multiplier(factor: int):
    def multiply(x: int) -> int:
        return x * factor
    return multiply

double = make_multiplier(2)
double(5)  # 10
```

## The Decorator Pattern

A decorator is a function that takes a function and returns a modified function. The `@decorator` syntax is syntactic sugar for `func = decorator(func)`. Understanding this desugaring is key to writing and debugging decorators. Always use `functools.wraps` on the wrapper function to preserve the original function's name, docstring, and module — without it, introspection and debugging break.

```python
import functools
import time

def timer(func):
    """Measure execution time of the decorated function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    """A deliberately slow function."""
    time.sleep(1)

slow_function()
# Without @functools.wraps: slow_function.__name__ would be "wrapper"
# With @functools.wraps: slow_function.__name__ is "slow_function"
```

## Parameterized Decorators

When a decorator needs configuration, you add an outer function that accepts parameters and returns the actual decorator. This three-level nesting (factory -> decorator -> wrapper) is the standard pattern. It can feel verbose, but each level has a clear purpose.

```python
import functools

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry a function on exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5)
def fetch_data(url: str) -> dict:
    ...
```

## Common Built-in Decorators

Python provides several decorators in the standard library that address frequent needs.

`@property` turns a method into a read-only attribute, enabling computed attributes with clean syntax. Use it to expose derived values or add validation to attribute access without changing the calling code.

`@staticmethod` defines a method that does not receive the instance or class as its first argument. Use it for utility functions that logically belong to the class namespace but do not need instance state.

`@classmethod` receives the class as its first argument (`cls`), making it useful for alternative constructors and factory methods that need to work correctly with inheritance.

`@functools.lru_cache` memoizes function results based on arguments. It is effective for pure functions with hashable arguments, especially recursive computations like Fibonacci or repeated expensive lookups.

```python
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class Circle:
    radius: float

    @property
    def area(self) -> float:
        """Computed attribute — no parentheses needed at call site."""
        import math
        return math.pi * self.radius ** 2

    @classmethod
    def from_diameter(cls, diameter: float) -> "Circle":
        """Alternative constructor."""
        return cls(radius=diameter / 2)

    @staticmethod
    def is_valid_radius(value: float) -> bool:
        """Utility — no instance or class state needed."""
        return value > 0

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

## Lambda Functions

Lambda expressions create small anonymous functions for use in contexts where defining a named function would be overkill. They are limited to a single expression. Use them for simple key functions in `sorted()`, `min()`, `max()`, and `filter()`. If the logic requires multiple statements or is complex enough to benefit from a name, use a regular `def` instead.

```python
# Sorting with a key function
users = [("Alice", 30), ("Bob", 25), ("Carol", 35)]
sorted(users, key=lambda u: u[1])  # Sort by age

# Prefer named functions for anything non-trivial
def sort_key(user: tuple[str, int]) -> int:
    return user[1]

sorted(users, key=sort_key)
```
