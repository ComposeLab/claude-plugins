# Comprehensions

Comprehensions are concise syntax for creating lists, dicts, and sets from iterables. They exist because transforming and filtering collections is so common that a dedicated syntax reduces boilerplate and communicates intent more clearly than an equivalent loop.

## List Comprehensions

A list comprehension builds a new list by applying an expression to each item in an iterable, optionally filtering with a condition. The pattern is `[expression for item in iterable if condition]`. List comprehensions are generally faster than equivalent `for` loops because the iteration happens at C level inside the Python interpreter.

```python
# Basic transformation
numbers = [1, 2, 3, 4, 5]
squares = [n ** 2 for n in numbers]  # [1, 4, 9, 16, 25]

# With filtering
evens = [n for n in numbers if n % 2 == 0]  # [2, 4]

# Transformation + filtering
even_squares = [n ** 2 for n in numbers if n % 2 == 0]  # [4, 16]

# Calling functions
names = ["alice", "bob", "carol"]
upper_names = [name.upper() for name in names]
```

## Dict Comprehensions

Dict comprehensions create dictionaries from iterables using `{key_expr: value_expr for item in iterable}`. They are useful for inverting mappings, building lookups from lists, and transforming dictionary values.

```python
# Building a lookup from a list of tuples
pairs = [("host", "localhost"), ("port", "8080")]
config = {k: v for k, v in pairs}

# Inverting a dictionary
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}  # {1: "a", 2: "b", 3: "c"}

# Filtering a dictionary
scores = {"alice": 95, "bob": 67, "carol": 82, "dan": 55}
passing = {name: score for name, score in scores.items() if score >= 70}
# {"alice": 95, "carol": 82}

# Transforming values
doubled = {k: v * 2 for k, v in scores.items()}
```

## Set Comprehensions

Set comprehensions use `{expression for item in iterable}` and produce a set with unique elements. They are useful when you need to collect distinct values from a transformation.

```python
# Collect unique first letters
words = ["apple", "avocado", "banana", "blueberry", "cherry"]
first_letters = {w[0] for w in words}  # {"a", "b", "c"}

# Unique lengths
lengths = {len(w) for w in words}  # {5, 7, 6, 9}
```

## Nested Comprehensions

Comprehensions can have multiple `for` clauses, which correspond to nested loops. The order reads left to right, matching how you would write the equivalent nested `for` statements. Use nested comprehensions sparingly — beyond two levels, a regular loop is almost always clearer.

```python
# Flattening a 2D list
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [x for row in matrix for x in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Equivalent loop (same order):
# for row in matrix:
#     for x in row:
#         flat.append(x)

# Cartesian product
colors = ["red", "blue"]
sizes = ["S", "M", "L"]
combos = [(c, s) for c in colors for s in sizes]
# [("red", "S"), ("red", "M"), ("red", "L"),
#  ("blue", "S"), ("blue", "M"), ("blue", "L")]
```

## Conditional Expressions in Comprehensions

The `if` clause at the end filters items. An `if/else` in the expression part transforms items conditionally. These are different positions with different purposes.

```python
numbers = [-3, -1, 0, 2, 5]

# Filter: only positive numbers
positive = [n for n in numbers if n > 0]  # [2, 5]

# Transform: conditional expression (ternary)
labels = ["positive" if n > 0 else "non-positive" for n in numbers]
# ["non-positive", "non-positive", "non-positive", "positive", "positive"]

# Combined: transform AND filter
clamped = [min(n, 3) for n in numbers if n > 0]  # [2, 3]
```

## When Comprehensions Are Better Than Loops

Comprehensions excel when the task is a simple transform, filter, or combination of both. They express "what" rather than "how," making the intent immediately clear. They also tend to be faster because they avoid repeated attribute lookups for `list.append`.

```python
# Comprehension is clearly better — simple transform
names = [user.name for user in users]

# Comprehension is clearly better — filter + transform
active_emails = [u.email for u in users if u.is_active]

# Comprehension with function call — still clear
parsed = [parse_line(line) for line in lines if line.strip()]
```

## When Loops Are Better

Loops are preferable when the body has side effects, requires multiple statements, needs error handling, or accumulates state in complex ways. Forcing these patterns into a comprehension sacrifices readability for brevity.

```python
# Side effects — use a loop
for user in users:
    send_notification(user)
    log_activity(user.id)

# Complex logic — use a loop
results = []
for item in data:
    try:
        parsed = parse(item)
    except ParseError:
        continue
    if parsed.is_valid():
        transformed = transform(parsed)
        results.append(transformed)

# Accumulating state — use a loop
total = 0
for transaction in transactions:
    if transaction.type == "credit":
        total += transaction.amount
    else:
        total -= transaction.amount
```

## The Readability Threshold

A comprehension should be readable in a single mental pass. If you need to re-read it multiple times to understand what it does, it has crossed the readability threshold and should become a loop or a helper function. As a rough guideline, comprehensions with more than two `for` clauses or more than one `if` condition start becoming hard to read.

```python
# On the edge — acceptable if the reader is familiar with the domain
pairs = [(x, y) for x in range(10) for y in range(10) if x != y]

# Too complex — refactor into a function or loop
# BAD:
result = {k: [v for v in vals if v > threshold]
          for k, vals in data.items()
          if any(v > threshold for v in vals)}

# BETTER:
def filter_above(data: dict, threshold: float) -> dict:
    result = {}
    for key, values in data.items():
        filtered = [v for v in values if v > threshold]
        if filtered:
            result[key] = filtered
    return result
```

## Walrus Operator (:=) in Comprehensions

The walrus operator (Python 3.8+) assigns a value to a variable as part of an expression. In comprehensions, it avoids computing an expensive expression twice — once for the filter and once for the output.

```python
# Without walrus — compute_score called twice per item
# results = [compute_score(x) for x in data if compute_score(x) > threshold]

# With walrus — compute_score called once per item
results = [score for x in data if (score := compute_score(x)) > threshold]

# Another practical example: filtering and capturing regex matches
import re
pattern = re.compile(r"\d+")
numbers = [int(m.group()) for line in lines if (m := pattern.search(line))]
```
