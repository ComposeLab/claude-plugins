---
name: algo-paradigms
description: Guides implementing algorithmic paradigms in Python including dynamic programming, greedy algorithms, backtracking, and string algorithms.
version: 1.0.0
author: composeLab
triggers:
  - "dynamic programming solution"
  - "greedy algorithm"
  - "backtracking approach"
  - "string matching algorithm"
  - "memoization in Python"
tags:
  - python
  - algorithms
  - dynamic-programming
  - greedy
  - backtracking
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# algo-paradigms

Assists with implementing algorithmic paradigms in Python. Covers dynamic programming (memoization and tabulation), greedy algorithms, backtracking, and string algorithms with complete implementations and analysis.

Always respond with complete, runnable Python code as the primary output. Never produce planning text, outlines, or narrative without accompanying code. For every implementation, include explicit state definitions, base cases, and the full algorithm — not pseudocode or partial sketches.

## Workflow: Write Code

### Step 1: Understand the Task

Identify the problem and determine which paradigm fits. Look for these signals:
- Overlapping subproblems + optimal substructure → dynamic programming
- Local optimal choice leads to global optimal → greedy
- Explore all possibilities with pruning → backtracking
- Pattern matching or text processing → string algorithms

Consult [Paradigm Selection](references/paradigm-selection.md) for the decision framework.

### Step 2: Implement

For DP problems, consult [Dynamic Programming](references/dynamic-programming.md) for memoization (top-down) and tabulation (bottom-up) approaches, state definition, and transition formulas.

For greedy and backtracking, consult [Greedy and Backtracking](references/greedy-backtracking.md) for proof of greedy correctness, backtracking templates, and pruning strategies.

For string problems, consult [String Algorithms](references/string-algorithms.md) for KMP, Rabin-Karp, edit distance, longest common subsequence, and other text processing algorithms.

Write a complete, runnable implementation. Include: explicit state definition and transition formula (for DP), base case handling, type hints, docstrings, and complexity annotations. Output the full code block as the primary response — not narrative or planning text.

### Step 3: Optimize

For DP: consider space optimization (rolling array, state compression). For backtracking: add pruning conditions to reduce the search space. Document the optimization in comments.

### Step 4: Review

Verify correctness with edge cases. For DP, verify the base cases and transition. For greedy, verify the greedy choice property holds. Present the result to the user.

## Workflow: Explain Concept

### Step 1: Identify the Topic

Determine which paradigm or specific algorithm the user wants to understand.

### Step 2: Teach the Concept

Consult the appropriate reference and use its precise terminology. Explain WHY the paradigm works for this class of problems, HOW to identify when to use it, and include a complete, runnable code example walking through a classic problem step by step.

### Step 3: Offer Follow-up

Suggest related problems or point to `algo-fundamentals` for complexity analysis or `algo-graphs-trees` for graph-based applications of these paradigms.
