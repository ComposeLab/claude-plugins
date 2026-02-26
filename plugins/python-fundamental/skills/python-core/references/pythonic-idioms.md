# Pythonic Idioms

Pythonic code leverages the language's features to be readable, concise, and expressive. These idioms exist because Python was designed with readability as a core value — there is usually one obvious way to do things, and experienced Python developers recognize these patterns instantly.

## Unpacking

Tuple unpacking assigns multiple variables from a sequence in one statement. Star unpacking (`*rest`) captures remaining elements into a list. Unpacking communicates that you know the structure of the data and makes the code self-documenting.

```python
# Basic unpacking
first, second, third = [1, 2, 3]

# Star unpacking — capture the rest
first, *middle, last = [1, 2, 3, 4, 5]
# first=1, middle=[2, 3, 4], last=5

# Swap without temporary variable
a, b = b, a

# Unpacking in function returns
def get_user():
    return "Alice", 30, "admin"

name, age, role = get_user()

# Nested unpacking
points = [(1, 2), (3, 4), (5, 6)]
for x, y in points:
    print(f"({x}, {y})")
```

## enumerate vs range(len())

`enumerate()` provides both the index and the value during iteration. It exists because `for i in range(len(items))` followed by `items[i]` is verbose, error-prone, and hides the intent. The `start` parameter lets you begin from an index other than zero.

```python
# WRONG — range(len()) is un-Pythonic
for i in range(len(names)):
    print(f"{i}: {names[i]}")

# RIGHT — enumerate is clear and direct
for i, name in enumerate(names):
    print(f"{i}: {name}")

# Start from 1 for human-readable numbering
for rank, player in enumerate(leaderboard, start=1):
    print(f"#{rank}: {player}")
```

## zip and zip_longest

`zip()` pairs elements from multiple iterables and stops at the shortest. It is the idiomatic way to iterate over parallel sequences. `itertools.zip_longest` pads shorter iterables with a fill value when you need all elements.

```python
names = ["Alice", "Bob", "Carol"]
scores = [95, 87, 92]

# Pair elements from parallel sequences
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# Build a dict from parallel lists
name_to_score = dict(zip(names, scores))

# zip_longest when lengths differ
from itertools import zip_longest
short = [1, 2]
long = [10, 20, 30]
list(zip_longest(short, long, fillvalue=0))
# [(1, 10), (2, 20), (0, 30)]

# Python 3.10+: strict mode raises on unequal lengths
# list(zip(short, long, strict=True))  # ValueError
```

## Dictionary Merging

Python 3.9+ introduced the `|` operator for merging dictionaries. It creates a new dict with values from the right operand taking precedence on key conflicts. The `|=` operator updates in place. For older versions, `{**d1, **d2}` or `d1.update(d2)` achieves the same result.

```python
defaults = {"host": "localhost", "port": 8080, "debug": False}
overrides = {"port": 9090, "debug": True}

# Python 3.9+ — merge operator
config = defaults | overrides
# {"host": "localhost", "port": 9090, "debug": True}

# In-place merge
defaults |= overrides

# Pre-3.9 equivalent
config = {**defaults, **overrides}
```

## Truthiness

Python objects have boolean value in conditional contexts. Empty collections, zero, `None`, and empty strings are falsy; everything else is truthy. Leveraging truthiness makes conditionals concise, but be careful to distinguish between "falsy" and "actually None" when the distinction matters.

```python
# Use truthiness for emptiness checks
items = []
if not items:  # Preferred over if len(items) == 0
    print("No items")

name = ""
if name:  # Preferred over if name != ""
    greet(name)

# When you specifically need to check for None, use `is`
result = find_item(query)
if result is None:  # Don't use `if not result` — 0 and [] are also falsy
    handle_missing()
```

## Ternary Expressions

The conditional expression `value_if_true if condition else value_if_false` replaces simple if/else assignments in a single line. Use it for straightforward choices. Avoid nesting ternaries — they become unreadable quickly.

```python
# Simple conditional assignment
status = "active" if user.is_enabled else "disabled"

# In f-strings
print(f"Found {count} {'item' if count == 1 else 'items'}")

# DON'T nest ternaries
# result = "a" if x > 0 else "b" if x == 0 else "c"  # Hard to read
```

## Chained Comparisons

Python allows chaining comparison operators, which maps directly to mathematical notation. `a < b < c` is equivalent to `a < b and b < c` but only evaluates `b` once. This is more readable and less error-prone than writing out the conjunction.

```python
# Chained comparison — clear and concise
if 0 <= score <= 100:
    process(score)

# Range check
if lower <= value < upper:
    print("In range")

# Multiple comparisons
if a < b < c < d:
    print("Strictly increasing")
```

## String Formatting with f-strings

F-strings (Python 3.6+) are the preferred string formatting method. They are evaluated at runtime, support arbitrary expressions, and are the fastest formatting option. Use format specs for alignment, padding, and number formatting.

```python
name = "Alice"
balance = 1234.5

# Basic interpolation
print(f"Hello, {name}!")

# Expressions inside braces
print(f"Balance: ${balance:,.2f}")  # Balance: $1,234.50

# Format specs
print(f"{'Name':<15} {'Score':>5}")  # Left and right alignment
print(f"{42:08b}")   # 00101010 — binary with zero padding
print(f"{0.123:.1%}")  # 12.3% — percentage formatting

# Debugging with = (Python 3.8+)
x, y = 10, 20
print(f"{x=}, {y=}")  # x=10, y=20
```

## Context Managers for Resource Management

The `with` statement ensures resources are properly cleaned up regardless of exceptions. Use it for files, locks, database connections, network sockets, and any resource that needs deterministic cleanup.

```python
# File handling
with open("output.txt", "w") as f:
    f.write("data")

# Multiple context managers (Python 3.10+ parenthesized form)
with (
    open("input.txt") as src,
    open("output.txt", "w") as dst,
):
    dst.write(src.read())

# Threading lock
import threading
lock = threading.Lock()
with lock:
    shared_resource.modify()
```

## __all__ for Module Exports

Define `__all__` at the module level to declare the public API. It controls what `from module import *` exports and serves as documentation of the intended public interface. Without `__all__`, all names not starting with underscore are exported.

```python
# mymodule.py
__all__ = ["PublicClass", "public_function"]

class PublicClass:
    ...

class _InternalHelper:
    ...

def public_function():
    ...

def _internal_helper():
    ...
```

## Avoid Mutable Default Arguments

Mutable defaults (lists, dicts, sets) are created once at function definition time and shared across all calls. This is one of Python's most common gotchas. The fix is to use `None` as the default and create the mutable object inside the function.

```python
# WRONG — the list is shared across calls
def add_item(item, items=[]):
    items.append(item)
    return items

# RIGHT — create a new list each call
def add_item(item, items: list | None = None) -> list:
    if items is None:
        items = []
    items.append(item)
    return items
```

## Use _ for Unused Variables

The underscore `_` is a convention for variables whose value you intentionally ignore. It signals to readers (and linters) that the value is not used. Use it in unpacking, loops, and comprehensions where some values are not needed.

```python
# Ignore index in enumerate
for _, name in enumerate(names):
    process(name)

# Ignore some unpacked values
_, _, extension = filename.rpartition(".")

# Loop a fixed number of times
for _ in range(5):
    retry_operation()
```

## EAFP Over LBYL

Python favors "Easier to Ask Forgiveness than Permission" — try the operation and catch the exception rather than checking preconditions. This avoids race conditions and is often more readable. See the Error Handling reference for detailed coverage.

```python
# EAFP — Pythonic
try:
    value = data[key]
except KeyError:
    value = default

# Even more concise for dicts
value = data.get(key, default)
```
