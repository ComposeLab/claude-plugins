# Greedy and Backtracking

Greedy algorithms and backtracking sit at opposite ends of the decision spectrum. Greedy commits to the locally best choice and never looks back. Backtracking explores all possibilities systematically, undoing choices that lead to dead ends. This reference covers both paradigms with complete implementations and the reasoning behind each approach.

## Greedy Algorithms

### Structure

Most greedy algorithms follow a three-step pattern: sort the input by some criterion, iterate through the sorted input making the locally optimal choice at each step, and build the solution incrementally. The sort criterion is the heart of the algorithm and must be chosen so that greedy choices lead to the global optimum.

### Proving Greedy Correctness: The Exchange Argument

A greedy algorithm is correct if you can show that any optimal solution can be transformed into the greedy solution without making it worse. The exchange argument works as follows: assume an optimal solution O differs from the greedy solution G. Find the first point of difference, and show that swapping O's choice for G's choice does not worsen O. Repeat until O equals G.

This proof technique matters because it is easy to write a greedy algorithm that looks right but fails on edge cases. If you cannot construct an exchange argument, the greedy approach is likely wrong.

### Activity Selection

Given activities with start and end times, select the maximum number of non-overlapping activities. The greedy strategy is to always pick the activity that finishes earliest, because it leaves the most room for subsequent activities.

```python
def activity_selection(activities: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Select maximum non-overlapping activities.
    Each activity is (start, end). O(n log n) time.

    The exchange argument: if an optimal solution picks an activity A that ends
    later than the greedy choice G, replacing A with G still leaves room for
    everything after A, so the solution is no worse.
    """
    sorted_acts = sorted(activities, key=lambda x: x[1])
    selected = [sorted_acts[0]]
    for start, end in sorted_acts[1:]:
        if start >= selected[-1][1]:
            selected.append((start, end))
    return selected
```

### Interval Scheduling: Minimum Meeting Rooms

A different greedy problem on intervals: given meetings, find the minimum number of rooms needed. This uses a sweep-line approach rather than the activity selection greedy.

```python
import heapq

def min_meeting_rooms(intervals: list[tuple[int, int]]) -> int:
    """Minimum meeting rooms needed. O(n log n) time.

    Sort by start time. Use a min-heap of end times to track rooms.
    If the earliest-ending room is free when a new meeting starts, reuse it.
    """
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])
    heap = [intervals[0][1]]  # end times of rooms in use
    for start, end in intervals[1:]:
        if heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)
    return len(heap)
```

### Fractional Knapsack

Unlike 0/1 knapsack (which requires DP), fractional knapsack allows taking fractions of items. Greedy by value-to-weight ratio works because you can always fill remaining capacity with the best available fraction.

```python
def fractional_knapsack(
    weights: list[float], values: list[float], capacity: float
) -> float:
    """Maximum value with fractional items allowed. O(n log n) time."""
    items = sorted(
        zip(weights, values),
        key=lambda x: x[1] / x[0],
        reverse=True,
    )
    total_value = 0.0
    for w, v in items:
        if capacity <= 0:
            break
        take = min(w, capacity)
        total_value += take * (v / w)
        capacity -= take
    return total_value
```

### Huffman Coding Concept

Huffman coding assigns shorter bit strings to more frequent characters. The greedy strategy repeatedly merges the two lowest-frequency nodes into a new node. This works because the two least frequent characters should have the longest codes, and making them siblings in the tree ensures they differ only in the last bit.

```python
import heapq
from typing import Optional

class HuffmanNode:
    def __init__(self, freq: int, char: Optional[str] = None,
                 left: Optional['HuffmanNode'] = None,
                 right: Optional['HuffmanNode'] = None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    def __lt__(self, other: 'HuffmanNode') -> bool:
        return self.freq < other.freq

def build_huffman_tree(freq_map: dict[str, int]) -> HuffmanNode:
    """Build a Huffman tree from character frequencies. O(n log n) time."""
    heap = [HuffmanNode(freq, char) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    return heap[0]

def huffman_codes(root: HuffmanNode, prefix: str = "") -> dict[str, str]:
    """Extract codes from Huffman tree by traversing left (0) and right (1)."""
    if root.char is not None:
        return {root.char: prefix or "0"}
    codes = {}
    if root.left:
        codes.update(huffman_codes(root.left, prefix + "0"))
    if root.right:
        codes.update(huffman_codes(root.right, prefix + "1"))
    return codes
```

## Backtracking

### The Choose-Explore-Unchoose Template

Backtracking follows a consistent template. At each step you choose an option, explore what follows from that choice recursively, then unchoose (undo) the option to try the next possibility. The power comes from pruning: skipping branches that cannot possibly lead to a valid or optimal solution.

```python
def backtrack(state, choices, result):
    if is_goal(state):
        result.append(state.copy())
        return
    for choice in choices:
        if is_valid(state, choice):   # pruning
            state.apply(choice)       # choose
            backtrack(state, choices, result)  # explore
            state.undo(choice)        # unchoose
```

### Permutations

Generate all permutations of a list. The state tracks which elements have been used.

```python
def permutations(nums: list[int]) -> list[list[int]]:
    """Generate all permutations. O(n! * n) time."""
    result: list[list[int]] = []
    used = [False] * len(nums)
    current: list[int] = []

    def backtrack() -> None:
        if len(current) == len(nums):
            result.append(current[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True          # choose
            current.append(nums[i])
            backtrack()             # explore
            current.pop()           # unchoose
            used[i] = False

    backtrack()
    return result
```

### Combinations

Generate all combinations of k elements from n. Pruning ensures we only pick elements in increasing index order to avoid duplicates.

```python
def combinations(nums: list[int], k: int) -> list[list[int]]:
    """Generate all C(n, k) combinations. O(C(n,k) * k) time."""
    result: list[list[int]] = []
    current: list[int] = []

    def backtrack(start: int) -> None:
        if len(current) == k:
            result.append(current[:])
            return
        # Pruning: need (k - len(current)) more elements,
        # so stop if not enough remain
        for i in range(start, len(nums) - (k - len(current)) + 1):
            current.append(nums[i])   # choose
            backtrack(i + 1)           # explore (i+1 avoids reuse)
            current.pop()             # unchoose

    backtrack(0)
    return result
```

### Subset Sum

Find all subsets that sum to a target. Pruning skips branches where the running sum already exceeds the target (assumes positive numbers).

```python
def subset_sum(nums: list[int], target: int) -> list[list[int]]:
    """Find all subsets summing to target. Assumes positive integers."""
    nums.sort()  # sorting enables pruning
    result: list[list[int]] = []
    current: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(nums)):
            if nums[i] > remaining:  # prune: sorted, so all after are too big
                break
            if i > start and nums[i] == nums[i - 1]:  # skip duplicates
                continue
            current.append(nums[i])
            backtrack(i + 1, remaining - nums[i])
            current.pop()

    backtrack(0, target)
    return result
```

### N-Queens

Place N queens on an NxN board so none attack each other. The pruning tracks which columns and diagonals are under attack.

```python
def solve_n_queens(n: int) -> list[list[str]]:
    """Find all valid N-Queens configurations. O(n!) time with pruning."""
    result: list[list[str]] = []
    queens: list[int] = []  # queens[row] = col
    cols = set()
    diag1 = set()  # row - col
    diag2 = set()  # row + col

    def backtrack(row: int) -> None:
        if row == n:
            board = []
            for r in range(n):
                line = '.' * queens[r] + 'Q' + '.' * (n - queens[r] - 1)
                board.append(line)
            result.append(board)
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue  # prune
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            queens.append(col)
            backtrack(row + 1)
            queens.pop()
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return result
```

### Sudoku Solver Pattern

Sudoku is a constraint satisfaction problem. The backtracking fills empty cells one at a time, trying digits 1-9 and pruning based on row, column, and box constraints.

```python
def solve_sudoku(board: list[list[int]]) -> bool:
    """Solve a Sudoku puzzle in-place. Empty cells are 0.
    Returns True if solved, False if no solution exists.
    """
    def is_valid(row: int, col: int, num: int) -> bool:
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        box_r, box_c = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if board[r][c] == num:
                    return False
        return True

    def backtrack() -> bool:
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    for num in range(1, 10):
                        if is_valid(r, c, num):
                            board[r][c] = num
                            if backtrack():
                                return True
                            board[r][c] = 0
                    return False  # no valid digit, backtrack
        return True  # all cells filled

    return backtrack()
```

## Pruning Strategies

Effective pruning is what makes backtracking practical. Common strategies include: sorting the input so you can break early when values exceed bounds, tracking used resources in sets for O(1) lookup instead of scanning, choosing the most constrained variable first (minimum remaining values heuristic in Sudoku), and detecting infeasibility early by checking partial constraints before recursing deeper.
