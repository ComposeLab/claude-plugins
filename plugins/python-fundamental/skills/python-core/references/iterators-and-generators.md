# Iterators and Generators

Iterators and generators are Python's mechanism for lazy evaluation — producing values one at a time instead of computing an entire collection upfront. This pattern is fundamental to writing memory-efficient code that can process datasets larger than available RAM.

## The Iterator Protocol

Any object that implements `__iter__()` and `__next__()` is an iterator. `__iter__` returns the iterator object itself, and `__next__` returns the next value or raises `StopIteration` when exhausted. The `for` loop is syntactic sugar that calls these methods automatically. Understanding this protocol explains why you can iterate over files, ranges, and custom objects.

```python
class Countdown:
    """An iterator that counts down from n to 1."""

    def __init__(self, n: int) -> None:
        self.current = n

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

# Usage — works with for loops, list(), etc.
for num in Countdown(5):
    print(num)  # 5, 4, 3, 2, 1
```

## Generator Functions

Generator functions use `yield` instead of `return`. When called, they return a generator object that implements the iterator protocol automatically. Each `yield` suspends the function's state, and the next call to `__next__` resumes from where it left off. This makes generators far simpler to write than manual iterator classes.

```python
def fibonacci():
    """Infinite Fibonacci sequence — lazy, no memory issue."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Take only what you need
from itertools import islice
first_ten = list(islice(fibonacci(), 10))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

## Generator Expressions

Generator expressions are the lazy equivalent of list comprehensions. They use parentheses instead of brackets and produce values one at a time. Use them when you need to iterate through results once, especially for large datasets where building a full list would waste memory.

```python
# List comprehension — builds entire list in memory
squares_list = [x ** 2 for x in range(1_000_000)]

# Generator expression — produces values lazily
squares_gen = (x ** 2 for x in range(1_000_000))

# Common use: passing to functions that consume iterables
total = sum(x ** 2 for x in range(1_000_000))  # No extra list
```

## yield from

The `yield from` expression delegates to a sub-iterator, forwarding all its values. It simplifies generators that combine multiple iterables and is essential for recursive generators (like tree traversal). Without `yield from`, you would need an explicit loop.

```python
def flatten(nested: list) -> list:
    """Recursively flatten nested lists."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3, 4], 5], 6]))
# [1, 2, 3, 4, 5, 6]

def chain_iterables(*iterables):
    """Yield all items from each iterable in sequence."""
    for it in iterables:
        yield from it

list(chain_iterables([1, 2], [3, 4], [5]))
# [1, 2, 3, 4, 5]
```

## send, throw, and close

Generators support bidirectional communication. `send(value)` resumes the generator and makes the `yield` expression evaluate to `value`. `throw(exception)` raises an exception at the point where the generator is paused. `close()` raises `GeneratorExit` inside the generator, allowing cleanup. These methods enable generators to function as coroutines, though for most use cases simple `yield` is sufficient.

```python
def accumulator():
    """A generator that accepts values via send() and yields running total."""
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value

gen = accumulator()
next(gen)          # Initialize — returns 0
gen.send(10)       # Returns 10
gen.send(20)       # Returns 30
gen.send(5)        # Returns 35
```

## itertools Module

The `itertools` module provides a toolkit of efficient iterator building blocks. These functions return iterators, so they compose well and use minimal memory.

```python
from itertools import (
    chain, islice, groupby, product,
    combinations, permutations, count, cycle, repeat,
    accumulate, starmap, filterfalse, takewhile, dropwhile,
)

# chain — concatenate iterables
list(chain([1, 2], [3, 4]))  # [1, 2, 3, 4]

# islice — slice an iterator (no negative indices)
list(islice(count(0), 5))  # [0, 1, 2, 3, 4]

# groupby — group consecutive elements by key (sort first!)
data = [("A", 1), ("A", 2), ("B", 3), ("B", 4)]
for key, group in groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# A [("A", 1), ("A", 2)]
# B [("B", 3), ("B", 4)]

# product — Cartesian product
list(product("AB", [1, 2]))
# [("A", 1), ("A", 2), ("B", 1), ("B", 2)]

# combinations and permutations
list(combinations("ABC", 2))   # [("A","B"), ("A","C"), ("B","C")]
list(permutations("AB", 2))    # [("A","B"), ("B","A")]

# Infinite iterators
# count(10)     → 10, 11, 12, 13, ...
# cycle("AB")   → A, B, A, B, A, B, ...
# repeat(42, 3) → 42, 42, 42
```

## functools.reduce

`reduce` applies a two-argument function cumulatively to items, reducing the iterable to a single value. It was moved from builtins to `functools` in Python 3 because explicit loops are often clearer. Use `reduce` for operations that naturally fold (like computing a product), but prefer `sum()`, `min()`, `max()`, or generator expressions when they apply.

```python
from functools import reduce
import operator

# Product of all elements
numbers = [1, 2, 3, 4, 5]
product = reduce(operator.mul, numbers)  # 120

# Prefer built-in alternatives when available
total = sum(numbers)       # Clearer than reduce(operator.add, ...)
largest = max(numbers)     # Clearer than reduce(max, ...)
```

## Memory-Efficient Patterns

Generators shine when processing data that does not fit in memory. Reading files line by line, streaming API responses, and processing database cursors are all natural fits for generators.

```python
def read_large_csv(path: str):
    """Process a CSV file line by line without loading it all."""
    with open(path) as f:
        header = next(f).strip().split(",")
        for line in f:
            values = line.strip().split(",")
            yield dict(zip(header, values))

# Process millions of rows with constant memory
for row in read_large_csv("huge_file.csv"):
    if float(row["amount"]) > 1000:
        process(row)

# Pipeline pattern — compose generators
def parse_lines(lines):
    for line in lines:
        yield line.strip().split(",")

def filter_valid(records):
    for record in records:
        if len(record) >= 3:
            yield record

def transform(records):
    for record in records:
        yield {"name": record[0], "value": float(record[1])}

# Each stage processes one item at a time
with open("data.csv") as f:
    pipeline = transform(filter_valid(parse_lines(f)))
    for item in pipeline:
        save(item)
```
