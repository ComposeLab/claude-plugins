# Graph Algorithms

This reference covers the core graph algorithms: traversals, shortest paths, minimum spanning trees, and structural queries. Each algorithm includes its key invariant (why it works), a complete Python implementation, and complexity analysis.

## BFS (Breadth-First Search)

BFS explores vertices in order of their distance from the source, measured in number of edges. It works because a queue processes vertices FIFO: all vertices at distance d are visited before any vertex at distance d+1. This makes BFS the natural choice for shortest paths in unweighted graphs.

```python
from collections import deque

def bfs(graph: dict[int, list[int]], start: int) -> dict[int, int]:
    """BFS traversal returning distances from start to all reachable vertices.

    Key invariant: when a vertex is dequeued, its recorded distance is final.

    Time: O(V + E)
    Space: O(V)
    """
    dist: dict[int, int] = {start: 0}
    queue: deque[int] = deque([start])
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist

def bfs_path(graph: dict[int, list[int]], start: int, end: int) -> list[int] | None:
    """Find shortest path (fewest edges) from start to end.

    Time: O(V + E)
    Space: O(V)
    """
    if start == end:
        return [start]
    parent: dict[int, int] = {start: -1}
    queue: deque[int] = deque([start])
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in parent:
                parent[v] = u
                if v == end:
                    path = []
                    while v != -1:
                        path.append(v)
                        v = parent[v]
                    return path[::-1]
                queue.append(v)
    return None
```

BFS also supports level-order processing, which is useful when you need to act on all vertices at the same distance before moving deeper.

```python
def bfs_levels(graph: dict[int, list[int]], start: int) -> list[list[int]]:
    """Return vertices grouped by BFS level (distance from start).

    Time: O(V + E)
    Space: O(V)
    """
    visited: set[int] = {start}
    levels: list[list[int]] = [[start]]
    frontier: list[int] = [start]
    while frontier:
        next_frontier: list[int] = []
        for u in frontier:
            for v in graph[u]:
                if v not in visited:
                    visited.add(v)
                    next_frontier.append(v)
        if next_frontier:
            levels.append(next_frontier)
        frontier = next_frontier
    return levels
```

## DFS (Depth-First Search)

DFS explores as deep as possible along each branch before backtracking. This naturally discovers structure that BFS misses: back edges reveal cycles, the finish order enables topological sorting, and the recursion tree maps to strongly connected components.

```python
def dfs_iterative(graph: dict[int, list[int]], start: int) -> list[int]:
    """Iterative DFS traversal returning visit order.

    Uses a stack instead of recursion to avoid stack overflow on deep graphs.

    Time: O(V + E)
    Space: O(V)
    """
    visited: set[int] = set()
    order: list[int] = []
    stack: list[int] = [start]
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        for v in graph[u]:
            if v not in visited:
                stack.append(v)
    return order

def dfs_recursive(graph: dict[int, list[int]], start: int) -> list[int]:
    """Recursive DFS traversal. Cleaner for problems needing backtracking logic.

    Time: O(V + E)
    Space: O(V) call stack
    """
    visited: set[int] = set()
    order: list[int] = []

    def _dfs(u: int) -> None:
        visited.add(u)
        order.append(u)
        for v in graph[u]:
            if v not in visited:
                _dfs(v)

    _dfs(start)
    return order
```

## Cycle Detection

In a directed graph, a cycle exists if DFS encounters a vertex that is currently on the recursion stack (a back edge). In an undirected graph, a cycle exists if DFS encounters a visited vertex that is not the parent of the current vertex.

```python
def has_cycle_directed(graph: dict[int, list[int]], vertices: list[int]) -> bool:
    """Detect cycle in a directed graph using DFS coloring.

    WHITE=0 (unvisited), GRAY=1 (in current path), BLACK=2 (fully processed).
    A back edge to a GRAY vertex proves a cycle.

    Time: O(V + E)
    Space: O(V)
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[int, int] = {v: WHITE for v in vertices}

    def _dfs(u: int) -> bool:
        color[u] = GRAY
        for v in graph.get(u, []):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and _dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(color[v] == WHITE and _dfs(v) for v in vertices)

def has_cycle_undirected(graph: dict[int, list[int]], vertices: list[int]) -> bool:
    """Detect cycle in an undirected graph.

    Time: O(V + E)
    Space: O(V)
    """
    visited: set[int] = set()

    def _dfs(u: int, parent: int) -> bool:
        visited.add(u)
        for v in graph.get(u, []):
            if v not in visited:
                if _dfs(v, u):
                    return True
            elif v != parent:
                return True
        return False

    return any(v not in visited and _dfs(v, -1) for v in vertices)
```

## Topological Sort

Topological sort orders vertices of a DAG so that every edge (u, v) has u before v. It works because DFS post-order (reversed) naturally respects dependencies: a vertex finishes only after all vertices reachable from it have finished.

```python
def topological_sort(graph: dict[int, list[int]], vertices: list[int]) -> list[int] | None:
    """Topological sort via DFS. Returns None if a cycle exists.

    Time: O(V + E)
    Space: O(V)
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[int, int] = {v: WHITE for v in vertices}
    order: list[int] = []

    def _dfs(u: int) -> bool:
        color[u] = GRAY
        for v in graph.get(u, []):
            if color.get(v, WHITE) == GRAY:
                return False  # cycle
            if color.get(v, WHITE) == WHITE and not _dfs(v):
                return False
        color[u] = BLACK
        order.append(u)
        return True

    for v in vertices:
        if color[v] == WHITE and not _dfs(v):
            return None
    return order[::-1]
```

## Dijkstra's Algorithm

Dijkstra finds shortest paths from a source to all other vertices in a graph with non-negative edge weights. The key invariant is greedy: the vertex with the smallest tentative distance is finalized next, because no future path through unvisited vertices can produce a shorter route (since all remaining edges are non-negative).

Python's `heapq` module provides the min-heap. Since `heapq` does not support decrease-key, we use the lazy deletion pattern: push updated distances and skip stale entries when popped.

```python
import heapq

def dijkstra(
    graph: dict[int, list[tuple[int, float]]], start: int
) -> tuple[dict[int, float], dict[int, int]]:
    """Dijkstra's shortest path algorithm.

    Returns (dist, parent) where dist maps each vertex to its shortest
    distance from start, and parent maps each vertex to its predecessor.

    Requires: all edge weights >= 0.

    Time: O((V + E) log V) with binary heap
    Space: O(V + E)
    """
    dist: dict[int, float] = {start: 0}
    parent: dict[int, int] = {start: -1}
    heap: list[tuple[float, int]] = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float('inf')):
            continue  # stale entry
        for v, w in graph.get(u, []):
            new_dist = d + w
            if new_dist < dist.get(v, float('inf')):
                dist[v] = new_dist
                parent[v] = u
                heapq.heappush(heap, (new_dist, v))

    return dist, parent

def reconstruct_path(parent: dict[int, int], end: int) -> list[int] | None:
    """Reconstruct path from Dijkstra's parent map."""
    if end not in parent:
        return None
    path: list[int] = []
    v = end
    while v != -1:
        path.append(v)
        v = parent[v]
    return path[::-1]
```

## Bellman-Ford Algorithm

Bellman-Ford handles graphs with negative edge weights, which Dijkstra cannot. It works by relaxing all edges V-1 times. After i iterations, the shortest path using at most i edges is correct. Since a shortest path in a graph with V vertices uses at most V-1 edges, V-1 iterations suffice. A V-th iteration that still relaxes an edge proves a negative cycle exists.

```python
def bellman_ford(
    vertices: list[int], edges: list[tuple[int, int, float]], start: int
) -> tuple[dict[int, float], bool]:
    """Bellman-Ford shortest path algorithm.

    Returns (dist, has_negative_cycle).

    Time: O(V * E)
    Space: O(V)
    """
    dist: dict[int, float] = {v: float('inf') for v in vertices}
    dist[start] = 0

    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Check for negative cycles
    has_negative_cycle = False
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    return dist, has_negative_cycle
```

## Kruskal's MST

Kruskal's algorithm builds a minimum spanning tree by greedily adding the cheapest edge that does not form a cycle. The correctness follows from the cut property: for any cut of the graph, the minimum weight edge crossing the cut belongs to some MST. Union-Find provides near-O(1) cycle detection per edge.

```python
class UnionFind:
    """Disjoint Set Union with path compression and union by rank.

    Time per operation: O(alpha(n)) amortized, effectively O(1).
    """
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True

def kruskal_mst(
    num_vertices: int, edges: list[tuple[int, int, float]]
) -> tuple[list[tuple[int, int, float]], float]:
    """Kruskal's MST algorithm.

    Returns (mst_edges, total_weight).

    Time: O(E log E) dominated by sorting
    Space: O(V + E)
    """
    edges_sorted = sorted(edges, key=lambda e: e[2])
    uf = UnionFind(num_vertices)
    mst: list[tuple[int, int, float]] = []
    total = 0.0

    for u, v, w in edges_sorted:
        if uf.union(u, v):
            mst.append((u, v, w))
            total += w
            if len(mst) == num_vertices - 1:
                break

    return mst, total
```

## Prim's MST

Prim's algorithm grows the MST from a starting vertex by repeatedly adding the cheapest edge connecting the tree to a non-tree vertex. Like Dijkstra, it uses a priority queue, but the key stored is the edge weight (not cumulative distance).

```python
def prim_mst(
    graph: dict[int, list[tuple[int, float]]], start: int = 0
) -> tuple[list[tuple[int, int, float]], float]:
    """Prim's MST algorithm using a priority queue.

    Returns (mst_edges, total_weight).

    Time: O((V + E) log V)
    Space: O(V + E)
    """
    visited: set[int] = set()
    mst: list[tuple[int, int, float]] = []
    total = 0.0
    # (weight, vertex, parent)
    heap: list[tuple[float, int, int]] = [(0, start, -1)]

    while heap:
        w, u, parent = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if parent != -1:
            mst.append((parent, u, w))
            total += w
        for v, weight in graph.get(u, []):
            if v not in visited:
                heapq.heappush(heap, (weight, v, u))

    return mst, total
```

## Connected Components

Finding connected components in an undirected graph is a direct application of BFS or DFS: start from an unvisited vertex, explore all reachable vertices (one component), repeat for remaining unvisited vertices.

```python
def connected_components(graph: dict[int, list[int]], vertices: list[int]) -> list[list[int]]:
    """Find all connected components in an undirected graph.

    Time: O(V + E)
    Space: O(V)
    """
    visited: set[int] = set()
    components: list[list[int]] = []

    for v in vertices:
        if v not in visited:
            component: list[int] = []
            queue: deque[int] = deque([v])
            visited.add(v)
            while queue:
                u = queue.popleft()
                component.append(u)
                for w in graph.get(u, []):
                    if w not in visited:
                        visited.add(w)
                        queue.append(w)
            components.append(component)

    return components
```

## Bipartite Check

A graph is bipartite if its vertices can be colored with two colors such that no adjacent vertices share a color. BFS naturally checks this: assign colors level by level. If an edge connects two same-colored vertices, the graph is not bipartite.

```python
def is_bipartite(graph: dict[int, list[int]], vertices: list[int]) -> bool:
    """Check if an undirected graph is bipartite using BFS coloring.

    Time: O(V + E)
    Space: O(V)
    """
    color: dict[int, int] = {}

    for start in vertices:
        if start in color:
            continue
        color[start] = 0
        queue: deque[int] = deque([start])
        while queue:
            u = queue.popleft()
            for v in graph.get(u, []):
                if v not in color:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    return False
    return True
```
