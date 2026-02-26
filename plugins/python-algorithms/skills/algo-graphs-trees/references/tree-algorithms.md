# Tree Algorithms

Trees are connected acyclic graphs, and their hierarchical structure enables efficient searching, sorting, and prefix matching. This reference covers binary tree traversals, binary search trees, AVL trees, heaps, and tries, with complete Python implementations.

## Binary Tree Node

All tree structures start from a node definition. Using a dataclass keeps the boilerplate minimal.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class TreeNode:
    val: Any
    left: TreeNode | None = None
    right: TreeNode | None = None
```

## Binary Tree Traversals

The four standard traversals each visit nodes in a different order, and each order is useful for different problems. Inorder on a BST yields sorted output. Preorder captures the tree structure (useful for serialization). Postorder processes children before parents (useful for deletion or computing subtree properties). Level-order processes by depth.

```python
from collections import deque

def inorder(root: TreeNode | None) -> list[Any]:
    """Left -> Root -> Right. On a BST, yields sorted order.

    Time: O(n), Space: O(h) where h is tree height.
    """
    result: list[Any] = []
    def _traverse(node: TreeNode | None) -> None:
        if node is None:
            return
        _traverse(node.left)
        result.append(node.val)
        _traverse(node.right)
    _traverse(root)
    return result

def preorder(root: TreeNode | None) -> list[Any]:
    """Root -> Left -> Right. Captures tree structure for serialization.

    Time: O(n), Space: O(h).
    """
    result: list[Any] = []
    def _traverse(node: TreeNode | None) -> None:
        if node is None:
            return
        result.append(node.val)
        _traverse(node.left)
        _traverse(node.right)
    _traverse(root)
    return result

def postorder(root: TreeNode | None) -> list[Any]:
    """Left -> Right -> Root. Processes children before parent.

    Time: O(n), Space: O(h).
    """
    result: list[Any] = []
    def _traverse(node: TreeNode | None) -> None:
        if node is None:
            return
        _traverse(node.left)
        _traverse(node.right)
        result.append(node.val)
    _traverse(root)
    return result

def level_order(root: TreeNode | None) -> list[list[Any]]:
    """BFS level-by-level traversal.

    Time: O(n), Space: O(n) for the queue at the widest level.
    """
    if root is None:
        return []
    result: list[list[Any]] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level: list[Any] = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

## Binary Search Tree (BST)

The BST invariant is simple: for every node, all values in its left subtree are smaller, and all values in its right subtree are larger. This invariant enables O(h) search, insert, and delete, where h is the tree height. In the best case h = O(log n) (balanced), but in the worst case h = O(n) (degenerate, like a linked list).

```python
class BST:
    """Binary Search Tree with insert, search, delete, min, and max.

    All operations are O(h) where h is tree height.
    """

    def __init__(self) -> None:
        self.root: TreeNode | None = None

    def insert(self, val: Any) -> None:
        """Insert a value, maintaining BST property."""
        self.root = self._insert(self.root, val)

    def _insert(self, node: TreeNode | None, val: Any) -> TreeNode:
        if node is None:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        # Duplicate values are ignored
        return node

    def search(self, val: Any) -> bool:
        """Return True if val exists in the tree."""
        return self._search(self.root, val)

    def _search(self, node: TreeNode | None, val: Any) -> bool:
        if node is None:
            return False
        if val == node.val:
            return True
        if val < node.val:
            return self._search(node.left, val)
        return self._search(node.right, val)

    def find_min(self) -> Any:
        """Return the minimum value. Follows left children to the bottom."""
        if self.root is None:
            raise ValueError("Tree is empty")
        node = self.root
        while node.left:
            node = node.left
        return node.val

    def find_max(self) -> Any:
        """Return the maximum value. Follows right children to the bottom."""
        if self.root is None:
            raise ValueError("Tree is empty")
        node = self.root
        while node.right:
            node = node.right
        return node.val

    def delete(self, val: Any) -> None:
        """Delete a value from the tree.

        Three cases:
        1. Leaf node: simply remove it.
        2. One child: replace node with its child.
        3. Two children: replace with inorder successor (smallest in right subtree),
           then delete the successor from the right subtree.
        """
        self.root = self._delete(self.root, val)

    def _delete(self, node: TreeNode | None, val: Any) -> TreeNode | None:
        if node is None:
            return None
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            # Found the node to delete
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Two children: find inorder successor
            successor = node.right
            while successor.left:
                successor = successor.left
            node.val = successor.val
            node.right = self._delete(node.right, successor.val)
        return node
```

## AVL Tree

An AVL tree is a self-balancing BST where the height difference between left and right subtrees (balance factor) is at most 1 for every node. When an insertion or deletion violates this, rotations restore balance. This guarantees O(log n) height, making all operations O(log n) worst-case.

There are four rotation cases. Left-left and right-right imbalances need a single rotation. Left-right and right-left imbalances need a double rotation (rotate the child first, then the node).

```python
class AVLNode:
    def __init__(self, val: Any) -> None:
        self.val = val
        self.left: AVLNode | None = None
        self.right: AVLNode | None = None
        self.height: int = 1

class AVLTree:
    """Self-balancing BST. All operations O(log n) guaranteed."""

    def __init__(self) -> None:
        self.root: AVLNode | None = None

    def _height(self, node: AVLNode | None) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: AVLNode) -> int:
        return self._height(node.left) - self._height(node.right)

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """Right rotation: y's left child becomes the new root of this subtree."""
        x = y.left
        assert x is not None
        t = x.right
        x.right = y
        y.left = t
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """Left rotation: x's right child becomes the new root of this subtree."""
        y = x.right
        assert y is not None
        t = y.left
        y.left = x
        x.right = t
        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        """Apply rotations if balance factor is outside [-1, 1]."""
        self._update_height(node)
        bf = self._balance_factor(node)

        if bf > 1:  # Left-heavy
            if self._balance_factor(node.left) < 0:  # Left-Right case
                node.left = self._rotate_left(node.left)  # type: ignore
            return self._rotate_right(node)

        if bf < -1:  # Right-heavy
            if self._balance_factor(node.right) > 0:  # Right-Left case
                node.right = self._rotate_right(node.right)  # type: ignore
            return self._rotate_left(node)

        return node

    def insert(self, val: Any) -> None:
        self.root = self._insert(self.root, val)

    def _insert(self, node: AVLNode | None, val: Any) -> AVLNode:
        if node is None:
            return AVLNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        else:
            return node  # no duplicates
        return self._rebalance(node)

    def search(self, val: Any) -> bool:
        node = self.root
        while node:
            if val == node.val:
                return True
            node = node.left if val < node.val else node.right
        return False
```

## Heap (Priority Queue)

A heap is a complete binary tree where every parent is smaller (min-heap) or larger (max-heap) than its children. Python's `heapq` module implements a min-heap on a plain list, where the element at index i has children at 2i+1 and 2i+2. The heap property guarantees O(1) access to the minimum and O(log n) insertion and extraction.

The `heapq` module is the standard tool for priority queues in Python. Understanding its interface avoids reinventing the wheel.

```python
import heapq

# Building a heap from an existing list: O(n) via sift-down
data = [5, 3, 8, 1, 2, 7]
heapq.heapify(data)  # data is now a valid min-heap: [1, 2, 7, 5, 3, 8]

# Push a new element: O(log n)
heapq.heappush(data, 4)

# Pop the smallest element: O(log n)
smallest = heapq.heappop(data)  # returns 1

# Peek at the smallest without removing: O(1)
current_min = data[0]

# Push and pop in one operation (more efficient than separate push+pop): O(log n)
result = heapq.heapreplace(data, 6)  # pops smallest, pushes 6

# Get the n smallest or largest elements: O(n log k)
three_smallest = heapq.nsmallest(3, data)
three_largest = heapq.nlargest(3, data)
```

Since `heapq` only provides a min-heap, simulate a max-heap by negating values on push and negating again on pop.

```python
class MaxHeap:
    """Max-heap wrapper around heapq (which is a min-heap).

    Negates values internally so the largest value is popped first.
    """

    def __init__(self) -> None:
        self._heap: list[float] = []

    def push(self, val: float) -> None:
        heapq.heappush(self._heap, -val)

    def pop(self) -> float:
        return -heapq.heappop(self._heap)

    def peek(self) -> float:
        return -self._heap[0]

    def __len__(self) -> int:
        return len(self._heap)
```

A common pattern is using heaps as priority queues with associated data. Tuples work well because Python compares them element by element.

```python
# Priority queue pattern: (priority, item)
pq: list[tuple[int, str]] = []
heapq.heappush(pq, (3, "low priority task"))
heapq.heappush(pq, (1, "high priority task"))
heapq.heappush(pq, (2, "medium priority task"))

priority, task = heapq.heappop(pq)  # (1, "high priority task")
```

## Trie (Prefix Tree)

A trie stores strings character by character along tree paths, enabling O(L) lookup, insertion, and prefix search where L is the string length. Tries are the right choice when you need prefix-based operations (autocomplete, spell checking, IP routing) because no comparison-based structure can match their prefix query performance.

Each node stores a dictionary of children (character -> node) and a flag indicating whether a complete word ends at that node.

```python
class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end: bool = False

class Trie:
    """Prefix tree supporting insert, search, and prefix queries.

    All operations are O(L) where L is the length of the word/prefix.
    Space: O(total characters across all inserted words) in the worst case,
    but shared prefixes reduce actual usage significantly.
    """

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        """Return True if the exact word exists in the trie."""
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """Return True if any word in the trie starts with the given prefix."""
        return self._find_node(prefix) is not None

    def _find_node(self, prefix: str) -> TrieNode | None:
        """Traverse the trie following the prefix. Returns None if prefix not found."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def words_with_prefix(self, prefix: str) -> list[str]:
        """Return all words in the trie that start with the given prefix.

        Useful for autocomplete features.
        """
        node = self._find_node(prefix)
        if node is None:
            return []
        result: list[str] = []
        self._collect_words(node, prefix, result)
        return result

    def _collect_words(self, node: TrieNode, current: str, result: list[str]) -> None:
        if node.is_end:
            result.append(current)
        for ch, child in node.children.items():
            self._collect_words(child, current + ch, result)
```

## When to Use Each Structure

**BST** is the right choice when you need ordered operations (find min, max, successor, range queries) and can tolerate O(n) worst-case if the input happens to be sorted. Use it as a learning structure or when you control the insertion order.

**AVL tree** guarantees O(log n) for all operations regardless of input order. Use it when worst-case performance matters and you need ordered operations. In practice, Python's `sortedcontainers` library often replaces hand-rolled balanced BSTs.

**Heap / Priority Queue** is optimal when you only need the minimum (or maximum) element, not arbitrary ordered access. Dijkstra's algorithm, event-driven simulation, and merge-k-sorted-lists all use heaps because they repeatedly need the current best element.

**Trie** is the right choice for prefix-based string operations. If you only need exact string lookup, a hash set is simpler and faster. Tries justify their memory overhead when you need prefix queries, lexicographic ordering, or character-by-character matching.
