# File I/O and Standard Library

Python's standard library provides battle-tested modules for file operations, data formats, collections, dates, text processing, logging, and type annotations. Reaching for the stdlib before third-party packages keeps dependencies minimal and code portable.

## File I/O with open()

Always use `open()` with a `with` statement to ensure files are closed even if an exception occurs. Specify the encoding explicitly for text files — Python 3 defaults to the platform's locale encoding, which varies. `"utf-8"` is the safe default for most use cases.

```python
# Reading text
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()       # Entire file as string
    # or
    lines = f.readlines()    # List of lines

# Reading line by line — memory efficient for large files
with open("large.txt", encoding="utf-8") as f:
    for line in f:
        process(line.rstrip("\n"))

# Writing text
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("first line\n")
    f.writelines(["second\n", "third\n"])

# Appending
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("new entry\n")

# Binary mode — for images, archives, etc.
with open("image.png", "rb") as f:
    header = f.read(8)

with open("copy.png", "wb") as f:
    f.write(data)
```

## pathlib.Path

The `pathlib` module (Python 3.4+) provides an object-oriented interface for filesystem paths. It replaces most uses of `os.path` with methods that are more readable and composable. Path objects work with `open()`, `os` functions, and most stdlib APIs.

```python
from pathlib import Path

# Building paths — / operator joins components
config_dir = Path.home() / ".config" / "myapp"
config_file = config_dir / "settings.json"

# Common operations
config_dir.mkdir(parents=True, exist_ok=True)
config_file.exists()
config_file.is_file()
config_file.suffix        # ".json"
config_file.stem          # "settings"
config_file.parent        # Path to directory

# Reading and writing shortcuts
text = config_file.read_text(encoding="utf-8")
config_file.write_text('{"key": "value"}', encoding="utf-8")

# Globbing
for py_file in Path("src").rglob("*.py"):
    print(py_file)

# Iterating directory contents
for item in config_dir.iterdir():
    if item.is_file():
        print(item.name)
```

## json Module

The `json` module serializes Python objects to JSON strings and deserializes JSON back to Python objects. It handles dicts, lists, strings, numbers, booleans, and None natively. For custom objects, provide a `default` function or subclass `JSONEncoder`.

```python
import json

# Serialize to string
data = {"name": "Alice", "scores": [95, 87, 92]}
json_str = json.dumps(data, indent=2)

# Deserialize from string
parsed = json.loads(json_str)

# File I/O
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

with open("data.json") as f:
    loaded = json.load(f)

# Custom serialization
from datetime import datetime

def serialize(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")

json.dumps({"time": datetime.now()}, default=serialize)
```

## csv Module

The `csv` module handles the complexities of CSV parsing (quoting, escaping, different delimiters). Use `csv.DictReader` for named column access and `csv.DictWriter` for writing structured data.

```python
import csv

# Reading with DictReader — columns become dict keys
with open("users.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["email"])

# Writing with DictWriter
users = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
]
with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "email"])
    writer.writeheader()
    writer.writerows(users)
```

## collections Module

The `collections` module provides specialized container types that extend the built-in dict, list, and tuple. Each type solves a specific pattern that would otherwise require boilerplate code.

```python
from collections import defaultdict, Counter, deque, namedtuple

# defaultdict — auto-creates missing entries
word_positions = defaultdict(list)
for i, word in enumerate(text.split()):
    word_positions[word].append(i)

# Counter — counting and frequency analysis
words = "the cat sat on the mat the cat".split()
freq = Counter(words)
freq.most_common(3)  # [("the", 3), ("cat", 2), ("sat", 1)]
freq["the"]          # 3

# deque — double-ended queue with O(1) append/pop on both ends
from collections import deque
buffer = deque(maxlen=100)  # Fixed-size buffer
buffer.append("event1")
buffer.appendleft("priority")
oldest = buffer.popleft()

# namedtuple — lightweight immutable records
Point = namedtuple("Point", ["x", "y"])
p = Point(3.0, 4.5)
print(p.x, p.y)  # Attribute access
x, y = p          # Unpacking works
```

## datetime and timedelta

The `datetime` module handles dates, times, and durations. Always use timezone-aware datetimes in production code to avoid subtle bugs. Python 3.9+ provides `zoneinfo` for IANA timezone support.

```python
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo  # Python 3.9+

# Current time — timezone aware
now = datetime.now(ZoneInfo("UTC"))

# Parsing and formatting
dt = datetime.strptime("2026-02-25", "%Y-%m-%d")
formatted = dt.strftime("%B %d, %Y")  # "February 25, 2026"

# Arithmetic with timedelta
tomorrow = date.today() + timedelta(days=1)
one_week_ago = datetime.now(ZoneInfo("UTC")) - timedelta(weeks=1)

# Comparing dates
if deadline > datetime.now(ZoneInfo("UTC")):
    print("Still time remaining")

# ISO format — best for serialization
iso_str = now.isoformat()  # "2026-02-25T10:30:00+00:00"
parsed_back = datetime.fromisoformat(iso_str)
```

## re (Regular Expressions)

The `re` module provides Perl-style regular expressions. Compile patterns that will be reused for better performance. Use raw strings (`r"..."`) for patterns to avoid backslash escaping issues.

```python
import re

# Search for a pattern
match = re.search(r"\d{3}-\d{4}", "Call 555-1234 today")
if match:
    print(match.group())  # "555-1234"

# Find all matches
emails = re.findall(r"[\w.]+@[\w.]+", text)

# Compiled pattern — faster when reused
pattern = re.compile(r"^(?P<name>\w+)\s+(?P<age>\d+)$", re.MULTILINE)
for m in pattern.finditer(data):
    print(m.group("name"), m.group("age"))

# Substitution
cleaned = re.sub(r"\s+", " ", messy_text)

# Split on pattern
parts = re.split(r"[,;]\s*", "a, b; c,d")  # ["a", "b", "c", "d"]
```

## logging Module

The `logging` module provides flexible event logging. Use it instead of `print()` for any output that should be configurable — different levels, formats, and destinations. Configure logging once at application startup, then use `getLogger(__name__)` in each module.

```python
import logging

# Configure once at startup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)

# Per-module logger
logger = logging.getLogger(__name__)

def process_data(data: list) -> list:
    logger.info("Processing %d items", len(data))
    results = []
    for item in data:
        try:
            results.append(transform(item))
        except ValueError:
            logger.warning("Skipping invalid item: %s", item)
    logger.debug("Processed %d/%d items", len(results), len(data))
    return results
```

## typing Module

Type hints document expected types and enable static analysis with tools like mypy. They do not affect runtime behavior but significantly improve code readability and IDE support.

```python
from typing import Optional, Union
from collections.abc import Sequence, Mapping, Callable, Iterator

# Basic type hints
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional — equivalent to X | None (Python 3.10+)
def find_user(user_id: int) -> Optional[dict]:
    ...

# Collections — use lowercase in Python 3.9+
def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Callable — functions as parameters
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# Union types — Python 3.10+ can use X | Y
def parse(value: str | int) -> float:
    return float(value)

# Type aliases
UserRecord = dict[str, str | int | list[str]]
Handler = Callable[[str], None]
```
