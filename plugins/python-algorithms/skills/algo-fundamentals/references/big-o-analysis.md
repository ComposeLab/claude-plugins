# Big-O Analysis

## Asymptotic Notation

Big-O notation describes the upper bound on an algorithm's growth rate as input size approaches infinity. When we say an algorithm is O(n), we mean its resource usage grows at most linearly with input size, ignoring constant factors and lower-order terms. This abstraction matters because constant factors depend on hardware and language, but growth rate determines whether an algorithm remains practical as data scales.

Big-Omega describes the lower bound (best an algorithm can do), and Big-Theta describes a tight bound (both upper and lower match). In practice, most discussions use Big-O because we usually care about the worst-case guarantee, but understanding all three prevents confusion when an algorithm has dramatically different best and worst cases.

## Common Complexity Classes

**O(1) - Constant time.** The operation takes the same time regardless of input size. Array index access and hash table lookup are canonical examples. The key insight is that no iteration over input occurs.

```python
def get_first(arr: list[int]) -> int:
    """Return the first element. O(1) time, O(1) space."""
    return arr[0]  # O(1) - direct index access
```

**O(log n) - Logarithmic time.** Each step eliminates a constant fraction of the remaining input, typically half. Binary search is the classic example. An input of 1 billion elements needs only about 30 steps because log2(10^9) is approximately 30. This class appears whenever a problem can be halved repeatedly.

```python
def binary_search(arr: list[int], target: int) -> int:
    """Find target index in sorted array. O(log n) time, O(1) space."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:  # O(log n) iterations - search space halves each time
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

**O(n) - Linear time.** The algorithm examines each element a constant number of times. Finding the maximum in an unsorted array requires looking at every element exactly once, so no algorithm can do better for this problem.

```python
def find_max(arr: list[int]) -> int:
    """Find maximum element. O(n) time, O(1) space."""
    result = arr[0]
    for x in arr:  # O(n) - must check every element
        if x > result:
            result = x
    return result
```

**O(n log n) - Linearithmic time.** This is the theoretical lower bound for comparison-based sorting. Merge sort and heap sort achieve this in worst case, while quicksort achieves it on average. Algorithms in this class typically divide the problem in half (log n levels) and do linear work at each level.

**O(n^2) - Quadratic time.** Usually arises from nested loops where both iterate over the input. Bubble sort, selection sort, and checking all pairs in an array fall here. Quadratic algorithms become impractical beyond roughly 10,000-50,000 elements depending on the constant factor.

```python
def has_duplicate_naive(arr: list[int]) -> bool:
    """Check for duplicates by comparing all pairs. O(n²) time, O(1) space."""
    n = len(arr)
    for i in range(n):          # O(n) outer
        for j in range(i + 1, n):  # O(n) inner
            if arr[i] == arr[j]:
                return True
    return False
```

**O(2^n) - Exponential time.** Each element doubles the work. The naive recursive Fibonacci and generating all subsets of a set are examples. These algorithms are only feasible for small inputs (n < 25-30 typically).

```python
def fib_naive(n: int) -> int:
    """Compute nth Fibonacci number. O(2^n) time, O(n) space (call stack)."""
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)  # Two recursive calls per level
```

**O(n!) - Factorial time.** Generating all permutations of n elements produces n! results. Brute-force solutions to the traveling salesman problem fall here. Only feasible for n < 12 or so.

## Analyzing Loops

**Single loop** over n elements contributes O(n). If the loop does constant work per iteration, the total is O(n). If each iteration does O(log n) work (e.g., a binary search inside), the total is O(n log n).

**Nested independent loops** multiply. Two nested loops each running n times yield O(n^2). Three nested loops yield O(n^3). The key word is "independent" -- each loop's bounds do not depend on the other's current value.

**Dependent nested loops** require more careful counting. When the inner loop runs `i` times for outer index `i`, the total is the sum 1 + 2 + ... + n = n(n+1)/2 = O(n^2). This pattern appears in insertion sort and building a triangular matrix.

```python
# Dependent nested loop: O(n²)
def sum_pairs(n: int) -> int:
    """Sum of i for all i in range(n). O(n²) total iterations."""
    total = 0
    for i in range(n):
        for j in range(i):  # Inner loop depends on outer variable
            total += 1
    return total  # Returns n*(n-1)/2
```

**Loops with multiplicative steps** (e.g., `i *= 2`) run O(log n) times because doubling reaches n in log2(n) steps. This is why binary search and divide-and-conquer splits are logarithmic.

```python
# Logarithmic loop: O(log n)
def count_doublings(n: int) -> int:
    count, i = 0, 1
    while i < n:
        i *= 2   # Doubling step
        count += 1
    return count  # Returns ceil(log2(n))
```

## Recursion Analysis

Recursive algorithms are analyzed using recurrence relations. The recurrence for merge sort is T(n) = 2T(n/2) + O(n): two subproblems of half size, plus linear merge work. Solving recurrences reveals the overall complexity.

**Master Theorem** provides a shortcut for recurrences of the form T(n) = aT(n/b) + O(n^d), where a is the number of subproblems, b is the factor by which input shrinks, and d is the exponent of the work done outside recursion. The three cases are:

- If d < log_b(a): T(n) = O(n^(log_b(a))). Recursion dominates.
- If d = log_b(a): T(n) = O(n^d * log n). Work is evenly split across levels.
- If d > log_b(a): T(n) = O(n^d). Top-level work dominates.

Merge sort has a=2, b=2, d=1. Since d = log_2(2) = 1, this is the second case: O(n log n).

For recurrences the Master Theorem does not cover (like Fibonacci's T(n) = T(n-1) + T(n-2)), draw the recursion tree and sum work across all nodes, or use substitution to prove a bound by induction.

## Amortized Analysis

Some operations are expensive occasionally but cheap most of the time. Amortized analysis averages the cost over a sequence of operations to give a more accurate picture.

The classic example is dynamic array append. Appending to a Python list is O(1) most of the time, but when the internal array is full, Python allocates a new array (typically 1.5x-2x the old size) and copies all elements, costing O(n). However, these expensive copies happen so infrequently that the average cost per append across n operations is still O(1). The intuition is that each cheap O(1) append "saves up" a small amount of work to pay for the occasional expensive resize.

```python
# Dynamic array append: O(1) amortized
data: list[int] = []
for i in range(n):
    data.append(i)  # O(1) amortized, O(n) worst-case single operation
# Total: O(n) for n appends, so O(1) per append amortized
```

## Space Complexity

Space complexity counts the extra memory an algorithm uses beyond the input. In-place algorithms like quicksort use O(log n) space for the recursion stack, while merge sort uses O(n) for temporary arrays. The distinction matters when memory is constrained.

Recursive algorithms always use at least O(depth) stack space. A recursion that goes n levels deep (like naive tree traversal on a skewed tree) uses O(n) space even if no explicit data structures are allocated.

## Best, Average, and Worst Case

These describe complexity across different inputs of the same size. Quicksort is O(n^2) worst case (already sorted input with bad pivot), O(n log n) average case (random input), and O(n log n) best case. Insertion sort is O(n) best case (already sorted), O(n^2) average and worst case.

Distinguishing cases matters for algorithm selection. If worst-case guarantees are critical (real-time systems, security-sensitive code), prefer algorithms with good worst-case bounds like merge sort over quicksort. If average performance matters more and worst case is rare, quicksort's smaller constant factors often win in practice.
