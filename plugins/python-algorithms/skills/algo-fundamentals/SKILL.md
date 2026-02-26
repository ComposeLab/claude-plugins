---
name: algo-fundamentals
description: Guides implementing and analyzing fundamental algorithms including sorting, searching, and Big-O complexity analysis in Python.
version: 1.0.0
author: composeLab
triggers:
  - "implement a sorting algorithm"
  - "analyze time complexity"
  - "Big-O notation"
  - "binary search implementation"
  - "algorithm complexity"
tags:
  - python
  - algorithms
  - sorting
  - searching
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# algo-fundamentals

Assists with implementing and analyzing fundamental algorithms in Python. Covers Big-O complexity analysis, sorting algorithms, and searching algorithms with complete implementations and complexity annotations.

Always respond with complete, runnable Python code. When explaining concepts, include code examples and use the precise definitions and terminology from the reference files. Never produce planning text or outlines without accompanying code.

## Workflow: Write Code

### Step 1: Understand the Task

Identify what the user needs: a specific algorithm implementation, algorithm selection for a problem, or performance optimization. Clarify input constraints (size, type, sorted/unsorted) if ambiguous.

### Step 2: Analyze Complexity Requirements

Consult [Big-O Analysis](references/big-o-analysis.md) for complexity classes, analysis techniques, and amortized analysis. Determine the target time and space complexity for the problem.

### Step 3: Implement

For sorting problems, consult [Sorting Algorithms](references/sorting-algorithms.md) for implementations of comparison-based and non-comparison sorts with their trade-offs.

For searching problems, consult [Searching Algorithms](references/searching-algorithms.md) for linear search, binary search variants, and search on specialized structures.

Write the implementation with:
- Type hints on function signatures
- Docstring explaining the algorithm and its complexity
- Time and space complexity as comments (e.g., `# O(n log n) time, O(n) space`)

### Step 4: Review

Verify correctness with edge cases (empty input, single element, duplicates, already sorted). Confirm the complexity matches the documented claim. Present the result to the user.

## Workflow: Explain Concept

### Step 1: Identify the Topic

Determine which algorithm or analysis concept the user wants to understand.

### Step 2: Teach the Concept

Consult the appropriate reference and use its exact definitions and terminology (e.g., Big-O as "upper bound on growth rate"). Explain WHY the algorithm works, HOW it achieves its complexity, and WHEN to choose it over alternatives. Include concrete code examples for each concept discussed and walk through a small example step by step.

### Step 3: Offer Follow-up

Suggest related algorithms or point to the `algo-graphs-trees` or `algo-paradigms` sibling skills for advanced topics.
