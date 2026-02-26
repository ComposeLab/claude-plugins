# Data Types and Structures

Python's type system is built around a small set of powerful built-in types. Understanding when to reach for each one prevents performance pitfalls and keeps code expressive.

## Scalar Types

Python has four primary scalar types. `int` has arbitrary precision, meaning it never overflows — this is why Python is popular for mathematical computation. `float` follows IEEE 754 double-precision, so it carries the usual floating-point caveats around equality comparison. `bool` is a subclass of `int` (True is 1, False is 0), which is why booleans work in arithmetic but also why you should test truthiness with `if value` rather than `if value == True`. `None` is a singleton representing absence of value; always test for it with `is None` rather than `== None` because `is` checks identity, which is both faster and semantically correct for singletons.

```python
# Arbitrary precision integers
big = 10 ** 100  # No overflow

# Float precision matters
0.1 + 0.2 == 0.3  # False — use math.isclose() instead

# None identity check
result = some_function()
if result is None:
    handle_missing()
```

## Strings

Strings are immutable sequences of Unicode code points. Immutability means every concatenation creates a new string object, so building strings in a loop with `+=` is O(n^2). Use `str.join()` or f-strings for construction. F-strings (Python 3.6+) are the preferred formatting approach because they are readable, fast, and evaluated at runtime.

```python
# Prefer join for building from parts
parts = ["hello", "world", "from", "python"]
result = " ".join(parts)

# F-strings for formatting
name, age = "Alice", 30
greeting = f"{name} is {age} years old"

# Useful string methods
"  hello  ".strip()          # "hello"
"hello world".split()        # ["hello", "world"]
"hello".startswith("he")     # True
",".join(["a", "b", "c"])    # "a,b,c"
```

## Sequences: list, tuple, range

Lists are mutable, ordered sequences — the workhorse collection in Python. Use them when you need to add, remove, or modify elements. Tuples are immutable sequences used for fixed collections of heterogeneous data (like returning multiple values from a function). The immutability of tuples makes them hashable (if all elements are hashable), so they can serve as dictionary keys or set members. Range objects are lazy sequences that generate integers on demand, using constant memory regardless of size.

```python
# List — mutable, for homogeneous collections
scores = [95, 87, 92, 88]
scores.append(91)
scores.sort(reverse=True)

# Tuple — immutable, for heterogeneous fixed records
point = (3.0, 4.5)
x, y = point  # Unpacking

# Range — lazy integer sequence
for i in range(1_000_000):  # Uses constant memory
    pass
```

## Mappings: dict and Variants

The built-in `dict` preserves insertion order (guaranteed since Python 3.7). It provides O(1) average-case lookups, making it the right choice for any key-value association. `defaultdict` from collections avoids KeyError by auto-creating missing entries with a factory function — use it when accumulating values (lists of items, running counts). `Counter` is purpose-built for counting hashable objects. `OrderedDict` is rarely needed now that dict preserves order, but it still offers `move_to_end()` and equality comparisons that consider order.

```python
from collections import defaultdict, Counter, OrderedDict

# dict — insertion-ordered key-value store
config = {"host": "localhost", "port": 8080}
config["debug"] = True

# defaultdict — auto-creates missing keys
groups = defaultdict(list)
for name, team in [("Alice", "A"), ("Bob", "B"), ("Carol", "A")]:
    groups[team].append(name)
# {"A": ["Alice", "Carol"], "B": ["Bob"]}

# Counter — counting elements
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counts = Counter(words)
counts.most_common(2)  # [("apple", 3), ("banana", 2)]
```

## Sets: set and frozenset

Sets are unordered collections of unique hashable elements with O(1) membership testing. Use them when you need to check membership, remove duplicates, or perform set algebra (union, intersection, difference). `frozenset` is the immutable variant, useful when you need a set as a dictionary key or a member of another set.

```python
# Deduplication
names = ["alice", "bob", "alice", "carol"]
unique = set(names)  # {"alice", "bob", "carol"}

# Set operations
admins = {"alice", "bob"}
editors = {"bob", "carol"}
admins & editors   # {"bob"} — intersection
admins | editors   # {"alice", "bob", "carol"} — union
admins - editors   # {"alice"} — difference

# Membership testing is O(1)
if "alice" in admins:
    grant_access()
```

## namedtuple vs dataclass

Both create structured data containers, but they serve different needs. `namedtuple` produces immutable, tuple-like objects that are memory-efficient and hashable by default. Use them for simple records where immutability is desirable. `dataclass` (Python 3.7+) produces mutable classes by default with more flexibility: default values, field factories, ordering, frozen mode, and post-init processing. Prefer dataclasses for domain models where you need methods or mutability.

```python
from typing import NamedTuple
from dataclasses import dataclass, field

# NamedTuple — lightweight immutable record
class Point(NamedTuple):
    x: float
    y: float

p = Point(3.0, 4.5)
# p.x = 1.0  # Error — immutable

# Dataclass — flexible, mutable by default
@dataclass
class User:
    name: str
    email: str
    roles: list[str] = field(default_factory=list)

    def is_admin(self) -> bool:
        return "admin" in self.roles

# Frozen dataclass — immutable and hashable
@dataclass(frozen=True)
class Config:
    host: str
    port: int = 8080
```

## Mutability and Type Conversion

Understanding mutability prevents a category of subtle bugs. Mutable objects (list, dict, set) can be changed in place, meaning multiple references to the same object see changes. Immutable objects (int, str, tuple, frozenset) create new objects on modification. This matters especially for default arguments — never use a mutable default because it is shared across all calls.

```python
# Mutable default argument trap
def bad_append(item, items=[]):  # WRONG — shared list
    items.append(item)
    return items

def good_append(item, items: list | None = None) -> list:
    if items is None:
        items = []
    items.append(item)
    return items

# Type conversion
int("42")         # 42
float("3.14")     # 3.14
str(42)           # "42"
list((1, 2, 3))   # [1, 2, 3]
tuple([1, 2, 3])  # (1, 2, 3)
dict([("a", 1)])  # {"a": 1}
set([1, 2, 2])    # {1, 2}
```
