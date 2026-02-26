# Searching Algorithms

## Linear Search

Linear search examines each element sequentially until the target is found or the collection is exhausted. It works on any iterable, sorted or unsorted, and requires no preprocessing.

The algorithm is the right choice when the data is unsorted, the collection is small, or you expect the target near the beginning. For a one-time search in unsorted data, nothing beats linear search since any algorithm must examine every element at least once.

```python
def linear_search(arr: list[int], target: int) -> int:
    """Find target by scanning. O(n) time, O(1) space."""
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

## Binary Search

Binary search works on sorted data by repeatedly comparing the target to the middle element and eliminating half the search space. The invariant is that if the target exists, it lies within the current `[lo, hi]` range. Each comparison halves the range, giving O(log n) time.

Binary search is one of the most important algorithms to internalize. The iterative version avoids recursion overhead and is less prone to stack overflow on large inputs. The key implementation detail is computing `mid` correctly: use `lo + (hi - lo) // 2` instead of `(lo + hi) // 2` to avoid integer overflow in languages with fixed-width integers (in Python this does not matter, but it is a good habit).

### Iterative Binary Search

```python
def binary_search(arr: list[int], target: int) -> int:
    """Find target in sorted array. O(log n) time, O(1) space."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

### Recursive Binary Search

The recursive version is cleaner for some but uses O(log n) stack space. It is useful when the recursive structure maps naturally to the problem (e.g., searching in a recursive data structure).

```python
def binary_search_recursive(
    arr: list[int], target: int, lo: int = 0, hi: int | None = None
) -> int:
    """Recursive binary search. O(log n) time, O(log n) space (stack)."""
    if hi is None:
        hi = len(arr) - 1
    if lo > hi:
        return -1

    mid = lo + (hi - lo) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, hi)
    else:
        return binary_search_recursive(arr, target, lo, mid - 1)
```

## Python's bisect Module

The `bisect` module provides C-implemented binary search for sorted lists. `bisect_left` returns the leftmost insertion point (first position where the element could be inserted to maintain order), and `bisect_right` returns the rightmost. These are the building blocks for finding first/last occurrences, counting elements in a range, and other sorted-array operations.

```python
import bisect

def find_with_bisect(arr: list[int], target: int) -> int:
    """Find target using bisect. O(log n) time, O(1) space."""
    idx = bisect.bisect_left(arr, target)
    if idx < len(arr) and arr[idx] == target:
        return idx
    return -1


def count_in_range(arr: list[int], lo_val: int, hi_val: int) -> int:
    """Count elements in [lo_val, hi_val] in sorted array. O(log n)."""
    left = bisect.bisect_left(arr, lo_val)
    right = bisect.bisect_right(arr, hi_val)
    return right - left
```

## Finding First and Last Occurrence

When an array contains duplicates, standard binary search may return any matching index. To find the first or last occurrence, modify the search to continue narrowing even after finding a match.

The insight for finding the first occurrence is: when `arr[mid] == target`, the answer could be `mid` or something to its left, so set `hi = mid - 1` and record `mid` as a candidate. For the last occurrence, set `lo = mid + 1` instead.

```python
def find_first(arr: list[int], target: int) -> int:
    """Find first occurrence of target. O(log n) time, O(1) space."""
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid       # Record candidate
            hi = mid - 1       # Keep searching left
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result


def find_last(arr: list[int], target: int) -> int:
    """Find last occurrence of target. O(log n) time, O(1) space."""
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid       # Record candidate
            lo = mid + 1       # Keep searching right
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

## Search in Rotated Sorted Array

A rotated sorted array (e.g., `[4, 5, 6, 7, 0, 1, 2]`) can still be searched in O(log n) by determining which half is properly sorted after computing `mid`. If the target falls within the sorted half, search there; otherwise, search the other half.

The invariant is that at least one of the two halves around `mid` is always sorted. By checking which half is sorted and whether the target lies within that half's range, we can decide which half to search next.

```python
def search_rotated(arr: list[int], target: int) -> int:
    """Search in rotated sorted array. O(log n) time, O(1) space."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid

        if arr[lo] <= arr[mid]:  # Left half is sorted
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                     # Right half is sorted
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

## Two-Pointer Technique

The two-pointer technique uses two indices that move through the data in a coordinated way, typically reducing an O(n^2) brute-force approach to O(n). The most common form places one pointer at each end of a sorted array and moves them inward based on a condition.

The classic application is finding two numbers in a sorted array that sum to a target. If the current sum is too small, advance the left pointer to increase it; if too large, retreat the right pointer to decrease it. The invariant is that no valid pair has been skipped because the eliminated positions cannot produce the target sum.

```python
def two_sum_sorted(arr: list[int], target: int) -> tuple[int, int] | None:
    """Find two indices whose values sum to target. O(n) time, O(1) space.
    Requires sorted input."""
    left, right = 0, len(arr) - 1
    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return (left, right)
        elif current_sum < target:
            left += 1   # Need larger sum
        else:
            right -= 1  # Need smaller sum
    return None
```

Other two-pointer applications include removing duplicates from a sorted array, merging two sorted arrays, and the container-with-most-water problem. The technique works whenever there is a monotonic relationship between pointer movement and the condition being checked.

## Sliding Window

The sliding window technique maintains a window (contiguous subarray) that expands or contracts to satisfy a condition. It reduces brute-force O(n^2) subarray enumeration to O(n) by reusing computation from the previous window position.

**Fixed-size window:** Compute the initial window's value, then slide by adding the new element and removing the old one.

```python
def max_sum_subarray(arr: list[int], k: int) -> int:
    """Find maximum sum of subarray of size k. O(n) time, O(1) space."""
    if len(arr) < k:
        return 0

    window_sum = sum(arr[:k])  # Initial window
    max_sum = window_sum

    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]  # Slide: add right, remove left
        max_sum = max(max_sum, window_sum)

    return max_sum
```

**Variable-size window:** Expand the right boundary until a condition is violated, then shrink the left boundary until the condition holds again. This pattern solves problems like finding the smallest subarray with sum >= target.

```python
def min_subarray_sum(arr: list[int], target: int) -> int:
    """Find length of smallest subarray with sum >= target. O(n) time, O(1) space."""
    n = len(arr)
    min_len = n + 1
    window_sum = 0
    left = 0

    for right in range(n):
        window_sum += arr[right]
        while window_sum >= target:  # Shrink from left
            min_len = min(min_len, right - left + 1)
            window_sum -= arr[left]
            left += 1

    return min_len if min_len <= n else 0
```

## Hash-Based Search

Python's `set` and `dict` provide O(1) average-case lookup using hash tables. When you need to check membership or find complements, converting to a set is often the fastest approach, trading O(n) space for O(1) per query.

The classic example is two-sum on unsorted data: for each element, check if its complement exists in a hash set. This achieves O(n) time versus O(n^2) for brute force or O(n log n) for sort-then-binary-search.

```python
def two_sum(arr: list[int], target: int) -> tuple[int, int] | None:
    """Find two indices whose values sum to target. O(n) time, O(n) space.
    Works on unsorted input."""
    seen: dict[int, int] = {}
    for i, val in enumerate(arr):
        complement = target - val
        if complement in seen:  # O(1) hash lookup
            return (seen[complement], i)
        seen[val] = i
    return None
```

## When to Use Each Approach

**Unsorted data, single query:** Linear search. No preprocessing needed.

**Unsorted data, many queries:** Build a hash set O(n) upfront, then O(1) per query. If ordering matters, sort first O(n log n) then binary search O(log n) per query.

**Sorted data:** Binary search or `bisect` module. Always prefer these over linear search when data is sorted.

**Pair/subarray problems on sorted data:** Two-pointer technique for O(n) solutions.

**Contiguous subarray optimization:** Sliding window for fixed or variable size windows.

**Membership testing or complement finding:** Hash set or dict for O(1) average lookup.

**Rotated or partially sorted data:** Modified binary search that identifies the sorted portion at each step.
