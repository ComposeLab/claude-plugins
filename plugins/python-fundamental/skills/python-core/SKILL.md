---
name: python-core
description: Guides writing idiomatic Python code covering data types, functions, OOP, error handling, generators, decorators, and standard library usage.
version: 1.0.0
author: composeLab
triggers:
  - "write Python code"
  - "explain Python concepts"
  - "use Python decorators"
  - "handle Python errors"
  - "Python best practices"
tags:
  - python
  - fundamentals
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# python-core

Assists with writing idiomatic Python code and explaining core language concepts. Covers data types, functions, decorators, OOP, error handling, generators, comprehensions, and standard library usage.

Always respond with complete, runnable Python code. Never produce planning text, outlines, or narrative without accompanying code. When the user asks to "design" or "explain" something, include a full code implementation as the primary response.

## Workflow: Write Code

### Step 1: Understand the Task

Identify what the user needs: a function, class, data transformation, file operation, or a combination. Clarify inputs, outputs, and constraints if ambiguous.

### Step 2: Choose the Right Approach

Consult [Data Types and Structures](references/data-types-and-structures.md) for choosing between lists, dicts, sets, tuples, namedtuples, and dataclasses based on the use case.

For function design, consult [Functions and Decorators](references/functions-and-decorators.md) for parameter patterns, closures, and decorator usage.

For class design, consult [OOP Patterns](references/oop-patterns.md) for inheritance, composition, protocols, ABCs, and dunder methods.

### Step 3: Write the Code

Output a complete, runnable Python code block as the primary response. Follow the conventions in [Pythonic Idioms](references/pythonic-idioms.md). Include type hints, docstrings, and all method implementations. Do not output planning text without code.

For list/dict/set transformations, prefer comprehensions when readable. Consult [Comprehensions](references/comprehensions.md) for when to use comprehensions vs loops.

For lazy evaluation and data pipelines, consult [Iterators and Generators](references/iterators-and-generators.md) for generator expressions, yield patterns, and itertools usage.

For file operations and common stdlib needs, consult [File I/O and Standard Library](references/file-io-and-stdlib.md).

### Step 4: Handle Errors

Consult [Error Handling](references/error-handling.md) for exception patterns, custom exceptions, context managers, and the EAFP vs LBYL distinction.

### Step 5: Review

Verify the code uses type hints, handles expected error cases, and follows Pythonic conventions. Present the result to the user.

For async or concurrency needs, direct the user to the `python-asyncio` or `python-concurrency` sibling skills.

## Workflow: Explain Concept

### Step 1: Identify the Topic

Determine which Python concept the user wants to understand. Map it to the relevant reference file.

### Step 2: Teach the Concept

Consult the appropriate reference and use its precise terminology and definitions in the explanation. Explain WHY the concept exists, HOW it works internally, and WHEN to use it. Include a complete, runnable code example as the primary content of the response.

### Step 3: Offer Follow-up

Suggest related concepts or practical applications. If the topic connects to async or concurrency, mention the sibling skills.
