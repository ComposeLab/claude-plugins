# Sorting Algorithms

## Comparison-Based Sorts

### Bubble Sort

Bubble sort repeatedly steps through the list, swapping adjacent elements if they are out of order. The name comes from the way larger elements "bubble" to the end of the array. Its invariant is that after pass k, the last k elements are in their final sorted positions.

This algorithm exists primarily for teaching purposes. Its O(n^2) average and worst-case performance makes it impractical for real data. The one redeeming quality is that it can detect an already-sorted list in O(n) by checking if any swaps occurred during a pass.

```python
def bubble_sort(arr: list[int]) -> list[int]:
    """Sort using adjacent swaps. O(n²) time, O(1) space."""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):  # Last i elements already sorted
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:  # O(n) best case: already sorted
            break
    return arr
```

### Selection Sort

Selection sort finds the minimum element in the unsorted portion and places it at the beginning. Its invariant is that the first k elements are the k smallest in sorted order after k passes. It always performs exactly n(n-1)/2 comparisons regardless of input, making its best, average, and worst cases all O(n^2).

Selection sort minimizes the number of swaps (exactly n-1), which matters when writes are expensive (e.g., flash memory). Otherwise, insertion sort is strictly preferable.

```python
def selection_sort(arr: list[int]) -> list[int]:
    """Sort by selecting minimums. O(n²) time, O(1) space. Not stable."""
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):  # Find minimum in unsorted portion
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]  # One swap per pass
    return arr
```

### Insertion Sort

Insertion sort builds the sorted portion one element at a time by inserting each new element into its correct position within the already-sorted prefix. The invariant is that elements before index k are sorted relative to each other after processing index k.

Insertion sort is the algorithm of choice for small arrays (n < 20-50) because its low overhead and good cache behavior outweigh its O(n^2) worst case. It is also optimal for nearly-sorted data, achieving O(n) when each element is at most a constant distance from its final position. This is why Timsort uses insertion sort for small runs.

```python
def insertion_sort(arr: list[int]) -> list[int]:
    """Sort by inserting into sorted prefix. O(n²) worst, O(n) best. Stable."""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:  # Shift elements right
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

### Merge Sort

Merge sort divides the array in half, recursively sorts each half, then merges the two sorted halves. The key insight is that merging two sorted arrays of total length n takes O(n) time and the recursion has log n levels, giving O(n log n) overall.

Merge sort guarantees O(n log n) in all cases (best, average, worst), which makes it the right choice when worst-case performance matters. It is stable, preserving the relative order of equal elements. The trade-off is O(n) auxiliary space for the merge step. For linked lists, merge sort is ideal because merging can be done in-place.

```python
def merge_sort(arr: list[int]) -> list[int]:
    """Divide-and-conquer sort. O(n log n) time, O(n) space. Stable."""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list[int], right: list[int]) -> list[int]:
    """Merge two sorted lists into one sorted list. O(n) time and space."""
    result: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= preserves stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### Quick Sort

Quicksort picks a pivot element, partitions the array into elements less than and greater than the pivot, then recursively sorts the partitions. The key insight is that the pivot ends up in its final sorted position after partitioning, and the two subproblems are independent.

Quicksort is O(n log n) on average but O(n^2) worst case (when the pivot is always the smallest or largest element). Randomized pivot selection reduces the probability of worst case to near zero. In practice, quicksort is often faster than merge sort due to better cache locality and lower constant factors, which is why many library sort implementations are quicksort-based or hybrid.

```python
import random


def quick_sort(arr: list[int]) -> list[int]:
    """Partition-based sort. O(n log n) average, O(n²) worst. Not stable."""
    if len(arr) <= 1:
        return arr

    pivot = arr[random.randint(0, len(arr) - 1)]  # Randomized pivot
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]
    return quick_sort(less) + equal + quick_sort(greater)


def quick_sort_inplace(arr: list[int], lo: int = 0, hi: int | None = None) -> None:
    """In-place quicksort using Lomuto partition. O(log n) space (stack)."""
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return

    pivot_idx = _partition(arr, lo, hi)
    quick_sort_inplace(arr, lo, pivot_idx - 1)
    quick_sort_inplace(arr, pivot_idx + 1, hi)


def _partition(arr: list[int], lo: int, hi: int) -> int:
    """Lomuto partition scheme. Pivot ends at its final sorted position."""
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    return i
```

### Heap Sort

Heap sort builds a max-heap from the array, then repeatedly extracts the maximum to build the sorted result from right to left. It guarantees O(n log n) in all cases with O(1) auxiliary space, making it useful when both time and space guarantees are needed.

The trade-off is poor cache performance compared to quicksort (heap operations jump around in memory) and it is not stable. In practice, heap sort is rarely the first choice but serves as a fallback guarantee in hybrid algorithms like introsort.

```python
def heap_sort(arr: list[int]) -> list[int]:
    """Sort using a max-heap. O(n log n) time, O(1) space. Not stable."""
    n = len(arr)

    # Build max-heap: O(n) using bottom-up heapify
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, n, i)

    # Extract elements: O(n log n)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # Move max to end
        _sift_down(arr, i, 0)

    return arr


def _sift_down(arr: list[int], size: int, root: int) -> None:
    """Restore heap property by sifting root down. O(log n)."""
    largest = root
    left, right = 2 * root + 1, 2 * root + 2

    if left < size and arr[left] > arr[largest]:
        largest = left
    if right < size and arr[right] > arr[largest]:
        largest = right

    if largest != root:
        arr[root], arr[largest] = arr[largest], arr[root]
        _sift_down(arr, size, largest)
```

## Non-Comparison Sorts

These algorithms break the O(n log n) lower bound for comparison-based sorting by exploiting properties of the data (integer keys, bounded range).

### Counting Sort

Counting sort works by counting occurrences of each value and using those counts to place elements directly. It requires knowing the range of values and uses O(k) extra space where k is the range. When k = O(n), counting sort achieves O(n) time.

This is the right choice for sorting integers within a known, small range (e.g., ages, grades, ASCII characters).

```python
def counting_sort(arr: list[int]) -> list[int]:
    """Sort integers with known range. O(n + k) time and space. Stable."""
    if not arr:
        return arr

    min_val, max_val = min(arr), max(arr)
    k = max_val - min_val + 1
    counts = [0] * k

    for x in arr:  # O(n) - count occurrences
        counts[x - min_val] += 1

    result: list[int] = []
    for i, count in enumerate(counts):  # O(k) - build result
        result.extend([i + min_val] * count)
    return result
```

### Radix Sort

Radix sort processes digits from least significant to most significant, using a stable sort (typically counting sort) as a subroutine for each digit. For d-digit numbers in base b, it runs in O(d * (n + b)) time. When d is constant (bounded number of digits), this becomes O(n).

Radix sort is ideal for sorting fixed-length strings, fixed-precision integers, or any data that can be decomposed into digits with bounded range.

```python
def radix_sort(arr: list[int]) -> list[int]:
    """Sort non-negative integers by digits. O(d*(n+b)) time. Stable."""
    if not arr:
        return arr

    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = _counting_sort_by_digit(arr, exp)
        exp *= 10
    return arr


def _counting_sort_by_digit(arr: list[int], exp: int) -> list[int]:
    """Stable sort by a specific digit position."""
    n = len(arr)
    output = [0] * n
    counts = [0] * 10

    for x in arr:
        digit = (x // exp) % 10
        counts[digit] += 1

    for i in range(1, 10):  # Cumulative counts for stability
        counts[i] += counts[i - 1]

    for i in range(n - 1, -1, -1):  # Place elements right-to-left
        digit = (arr[i] // exp) % 10
        counts[digit] -= 1
        output[counts[digit]] = arr[i]

    return output
```

## Python's Built-in Sort: Timsort

Python's `sorted()` and `list.sort()` use Timsort, a hybrid algorithm that combines merge sort and insertion sort. Timsort identifies existing sorted runs in the data and merges them efficiently, achieving O(n) on already-sorted or nearly-sorted input and O(n log n) worst case. It is stable and uses O(n) space.

For nearly all practical Python sorting needs, use the built-in sort. It is implemented in C, highly optimized, and handles edge cases. Write a custom sort only when you need a fundamentally different algorithm (e.g., counting sort for bounded integers) or when you need to understand the algorithm for educational purposes.

```python
# Built-in sort: O(n log n) time, O(n) space. Stable.
arr = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_arr = sorted(arr)          # Returns new list, original unchanged
arr.sort()                         # Sorts in-place, returns None
arr.sort(key=lambda x: -x)        # Sort descending using key function
```

## Comparison Table

| Algorithm      | Best       | Average    | Worst      | Space  | Stable | In-place |
|----------------|------------|------------|------------|--------|--------|----------|
| Bubble Sort    | O(n)       | O(n^2)     | O(n^2)     | O(1)   | Yes    | Yes      |
| Selection Sort | O(n^2)     | O(n^2)     | O(n^2)     | O(1)   | No     | Yes      |
| Insertion Sort | O(n)       | O(n^2)     | O(n^2)     | O(1)   | Yes    | Yes      |
| Merge Sort     | O(n log n) | O(n log n) | O(n log n) | O(n)   | Yes    | No       |
| Quick Sort     | O(n log n) | O(n log n) | O(n^2)     | O(log n)| No    | Yes      |
| Heap Sort      | O(n log n) | O(n log n) | O(n log n) | O(1)   | No     | Yes      |
| Counting Sort  | O(n + k)   | O(n + k)   | O(n + k)   | O(k)   | Yes    | No       |
| Radix Sort     | O(dn)      | O(dn)      | O(dn)      | O(n+k) | Yes    | No       |
| Timsort        | O(n)       | O(n log n) | O(n log n) | O(n)   | Yes    | No       |

## When to Use Each

**Default choice:** Use Python's built-in `sorted()` or `list.sort()`. Timsort is fast, stable, and adaptive.

**Small arrays (n < 50):** Insertion sort is competitive due to low overhead. Timsort already uses insertion sort internally for small runs, so the built-in sort handles this automatically.

**Nearly sorted data:** Insertion sort is O(n) for data where elements are close to their final positions. Timsort also excels here by detecting existing runs.

**Guaranteed O(n log n) needed:** Merge sort or heap sort. Merge sort is stable; heap sort uses O(1) space.

**Average-case performance priority:** Quicksort has excellent cache behavior and small constant factors. Use randomized pivot to avoid O(n^2) worst case.

**Integer keys with bounded range:** Counting sort for small ranges, radix sort for larger integers with fixed digit count. Both beat the O(n log n) comparison lower bound.

**Stability required:** Merge sort, insertion sort, counting sort, radix sort, or Timsort. Quicksort and heap sort are not stable.

**Memory constrained:** Heap sort (O(1) space) or in-place quicksort (O(log n) stack space). Merge sort's O(n) space can be prohibitive for very large arrays.
