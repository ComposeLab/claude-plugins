# Graph Representations

Choosing the right graph representation determines how naturally you can express algorithms and how efficiently they run. The three standard representations each optimize for different access patterns, and understanding their trade-offs prevents you from fighting the data structure instead of solving the problem.

## Adjacency List

The adjacency list is the default choice for most graph problems. It maps each vertex to a collection of its neighbors, which means you only store edges that actually exist. For sparse graphs (where E is much less than V^2), this keeps memory proportional to the graph's actual size rather than its theoretical maximum.

Python's `defaultdict(list)` is the idiomatic way to build an adjacency list because it handles missing keys gracefully during construction.

```python
from collections import defaultdict

def build_adjacency_list(edges: list[tuple[int, int]], directed: bool = False) -> dict[int, list[int]]:
    """Build an adjacency list from a list of edges.

    Time: O(E) to build
    Space: O(V + E)
    """
    graph: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    return graph
```

Iterating over all neighbors of a vertex takes O(degree(v)) time, which is optimal since you must examine each neighbor. Checking whether a specific edge (u, v) exists requires scanning u's neighbor list, taking O(degree(u)) time. If you need O(1) edge lookups while keeping the adjacency list structure, use `defaultdict(set)` instead.

```python
def build_adjacency_set(edges: list[tuple[int, int]], directed: bool = False) -> dict[int, set[int]]:
    """Adjacency list using sets for O(1) edge existence checks.

    Trade-off: slightly more memory per entry, but O(1) edge lookup.
    """
    graph: dict[int, set[int]] = defaultdict(set)
    for u, v in edges:
        graph[u].add(v)
        if not directed:
            graph[v].add(u)
    return graph
```

## Weighted Adjacency List

For weighted graphs, store the weight alongside each neighbor. Tuples `(neighbor, weight)` are the simplest approach. Some algorithms (Dijkstra, Bellman-Ford) need the weight during relaxation, so having it directly in the neighbor list avoids a separate weight lookup.

```python
def build_weighted_adjacency_list(
    edges: list[tuple[int, int, float]], directed: bool = False
) -> dict[int, list[tuple[int, float]]]:
    """Build a weighted adjacency list from (u, v, weight) edges.

    Time: O(E)
    Space: O(V + E)
    """
    graph: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
        if not directed:
            graph[v].append((u, w))
    return graph
```

## Adjacency Matrix

The adjacency matrix represents the graph as a V x V grid where entry `matrix[i][j]` indicates whether an edge exists from vertex i to vertex j (and its weight, if applicable). This representation shines for dense graphs where most vertex pairs are connected, because you pay V^2 space regardless of edge count, so you might as well have the edges to justify it.

The key advantage is O(1) edge existence checks. The key disadvantage is O(V) time to enumerate a vertex's neighbors (you must scan an entire row), and O(V^2) space even for sparse graphs.

```python
def build_adjacency_matrix(
    num_vertices: int, edges: list[tuple[int, int]], directed: bool = False
) -> list[list[int]]:
    """Build an adjacency matrix. Uses 0/1 for unweighted graphs.

    Time: O(V^2 + E) to build
    Space: O(V^2)
    """
    matrix = [[0] * num_vertices for _ in range(num_vertices)]
    for u, v in edges:
        matrix[u][v] = 1
        if not directed:
            matrix[v][u] = 1
    return matrix

def build_weighted_matrix(
    num_vertices: int, edges: list[tuple[int, int, float]], directed: bool = False
) -> list[list[float]]:
    """Build a weighted adjacency matrix. Uses float('inf') for no edge.

    Time: O(V^2 + E)
    Space: O(V^2)
    """
    INF = float('inf')
    matrix = [[INF] * num_vertices for _ in range(num_vertices)]
    for i in range(num_vertices):
        matrix[i][i] = 0
    for u, v, w in edges:
        matrix[u][v] = w
        if not directed:
            matrix[v][u] = w
    return matrix
```

## Edge List

The edge list is simply a collection of `(u, v)` or `(u, v, weight)` tuples. It uses minimal structure and is the natural input format for algorithms that process edges independently, such as Kruskal's MST algorithm which sorts edges by weight and processes them one at a time.

```python
# Unweighted edge list
edges: list[tuple[int, int]] = [(0, 1), (0, 2), (1, 3), (2, 3)]

# Weighted edge list
weighted_edges: list[tuple[int, int, float]] = [(0, 1, 4.0), (0, 2, 1.0), (1, 3, 2.0), (2, 3, 5.0)]

# Sorting by weight for Kruskal's
sorted_edges = sorted(weighted_edges, key=lambda e: e[2])
```

Edge lists are poor for neighbor lookups (O(E) to find all neighbors of a vertex) but excellent when the algorithm only needs to iterate over all edges.

## Converting Between Representations

Algorithms sometimes need a different representation than what you start with. These conversions are straightforward.

```python
def adj_list_to_matrix(adj: dict[int, list[int]], num_vertices: int) -> list[list[int]]:
    """Convert adjacency list to adjacency matrix. O(V^2 + E)."""
    matrix = [[0] * num_vertices for _ in range(num_vertices)]
    for u in adj:
        for v in adj[u]:
            matrix[u][v] = 1
    return matrix

def adj_list_to_edge_list(adj: dict[int, list[int]], directed: bool = False) -> list[tuple[int, int]]:
    """Convert adjacency list to edge list. O(V + E)."""
    edges = []
    seen: set[tuple[int, int]] = set()
    for u in adj:
        for v in adj[u]:
            edge = (u, v) if directed else (min(u, v), max(u, v))
            if edge not in seen:
                seen.add(edge)
                edges.append(edge)
    return edges
```

## Space Complexity Comparison

| Representation    | Space     | Edge check | Neighbors  | Best for              |
|-------------------|-----------|------------|------------|-----------------------|
| Adjacency list    | O(V + E)  | O(deg(v))  | O(deg(v))  | Sparse graphs, BFS/DFS|
| Adjacency set     | O(V + E)  | O(1)       | O(deg(v))  | Sparse + edge queries |
| Adjacency matrix  | O(V^2)    | O(1)       | O(V)       | Dense graphs          |
| Edge list         | O(E)      | O(E)       | O(E)       | Edge-centric algorithms|

When in doubt, start with an adjacency list. It handles the vast majority of graph problems efficiently and converts easily to other representations when needed.
