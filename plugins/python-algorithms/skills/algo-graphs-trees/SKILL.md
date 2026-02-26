---
name: algo-graphs-trees
description: Guides implementing graph and tree algorithms in Python including traversals, shortest paths, spanning trees, and balanced search trees.
version: 1.0.0
author: composeLab
triggers:
  - "implement graph algorithm"
  - "BFS or DFS traversal"
  - "shortest path algorithm"
  - "binary search tree"
  - "tree data structure"
tags:
  - python
  - algorithms
  - graphs
  - trees
requires:
  - python3
invocation:
  user_invocable: true
  auto_invoke: true
---

# algo-graphs-trees

Assists with implementing graph and tree algorithms in Python. Covers graph representations, traversals, shortest path algorithms, minimum spanning trees, binary search trees, heaps, and tries.

## Workflow: Write Code

### Step 1: Understand the Task

Identify the problem type: graph traversal, shortest path, connectivity, tree operations, or data structure implementation. Clarify whether the graph is directed/undirected, weighted/unweighted, and the expected scale.

### Step 2: Choose the Representation

Consult [Graph Representations](references/graph-representations.md) for adjacency list, adjacency matrix, and edge list trade-offs. Choose based on graph density and the operations needed.

### Step 3: Implement

For graph algorithms (BFS, DFS, Dijkstra, Bellman-Ford, MST), consult [Graph Algorithms](references/graph-algorithms.md) for complete implementations with complexity analysis.

For tree data structures (BST, AVL, heap, trie), consult [Tree Algorithms](references/tree-algorithms.md) for implementations and balancing strategies.

Write the implementation with type hints, docstrings, and complexity annotations.

### Step 4: Review

Verify correctness with edge cases (disconnected graph, single node, cycles, empty tree). Confirm the complexity matches the algorithm's known bounds. Present the result to the user.

## Workflow: Explain Concept

### Step 1: Identify the Topic

Determine which graph or tree concept the user wants to understand.

### Step 2: Teach the Concept

Consult the appropriate reference and explain WHY the algorithm works (key invariant or proof sketch), HOW it traverses or builds the structure, and WHEN to choose it. Walk through a small example.

### Step 3: Offer Follow-up

Suggest related algorithms or point to `algo-fundamentals` for complexity analysis or `algo-paradigms` for the underlying technique (greedy, DP).
