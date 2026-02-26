# Dynamic Programming

Dynamic programming transforms exponential recursive problems into polynomial ones by storing solutions to subproblems. The core insight is simple: if you solve the same subproblem multiple times, solve it once and remember the answer. This reference covers both implementation approaches, state design, and classic problems with complete Python code.

## Two Approaches: Memoization vs Tabulation

Memoization (top-down) starts from the original problem and recurses downward, caching results as they are computed. Tabulation (bottom-up) fills a table starting from the smallest subproblems and builds up to the answer. Both achieve the same asymptotic complexity. Memoization is often easier to write because it mirrors the recursive thinking, while tabulation avoids recursion overhead and makes space optimization more straightforward.

## Memoization with @lru_cache

Python's `functools.lru_cache` provides the simplest memoization. It works with functions whose arguments are hashable. For problems with small state spaces, this is the fastest way to write a DP solution.

```python
from functools import lru_cache

def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number. O(n) time, O(n) space."""
    @lru_cache(maxsize=None)
    def fib(k: int) -> int:
        if k <= 1:
            return k
        return fib(k - 1) + fib(k - 2)
    return fib(n)
```

## Memoization with Manual Dictionary

When arguments are not hashable (lists, for instance) or when you need finer control over the cache, use a dictionary. Convert unhashable arguments to tuples for use as keys.

```python
def coin_change_memo(coins: list[int], amount: int) -> int:
    """Minimum coins to make amount. Returns -1 if impossible.
    O(amount * len(coins)) time, O(amount) space.
    """
    memo: dict[int, int] = {}

    def dp(remaining: int) -> int:
        if remaining == 0:
            return 0
        if remaining < 0:
            return float('inf')
        if remaining in memo:
            return memo[remaining]
        result = min(dp(remaining - c) + 1 for c in coins)
        memo[remaining] = result
        return result

    ans = dp(amount)
    return ans if ans != float('inf') else -1
```

## Tabulation (Bottom-Up)

Tabulation iterates through states in a defined order, filling a table. The key is ensuring that when you compute `dp[i]`, all states it depends on are already computed.

```python
def coin_change_tab(coins: list[int], amount: int) -> int:
    """Minimum coins to make amount using tabulation.
    O(amount * len(coins)) time, O(amount) space.
    """
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i and dp[i - c] + 1 < dp[i]:
                dp[i] = dp[i - c] + 1
    return dp[amount] if dp[amount] != float('inf') else -1
```

## State Definition Strategy

Defining the state is the hardest part of DP. The state must capture enough information to make optimal decisions for the remaining subproblem. A good approach is to ask: "What information do I need to know at this point to solve the rest of the problem?"

For sequence problems, the state is often `dp[i]` representing the answer for the first `i` elements. For two-sequence problems (LCS, edit distance), the state is `dp[i][j]` for prefixes of length `i` and `j`. For knapsack-style problems, the state includes both the item index and the remaining capacity: `dp[i][w]`.

## Transition Formula Writing

The transition formula defines how `dp[i]` relates to smaller subproblems. Write it by considering all possible last decisions. For coin change, the last coin used could be any coin `c`, so `dp[i] = min(dp[i - c] + 1)` for all valid `c`. For LCS, the last characters either match or they do not, giving two cases.

## 0/1 Knapsack

```python
def knapsack_01(weights: list[int], values: list[int], capacity: int) -> int:
    """Maximum value achievable with given capacity.
    O(n * capacity) time, O(n * capacity) space.
    """
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]  # skip item i
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)
    return dp[n][capacity]
```

### Space-Optimized Knapsack (Rolling Array)

Because each row only depends on the previous row, we can use a single 1D array. The trick is iterating capacity in reverse to avoid using updated values from the current row.

```python
def knapsack_01_optimized(weights: list[int], values: list[int], capacity: int) -> int:
    """Space-optimized 0/1 knapsack. O(n * capacity) time, O(capacity) space."""
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]
```

## Longest Common Subsequence

```python
def lcs(s1: str, s2: str) -> int:
    """Length of longest common subsequence. O(mn) time, O(mn) space."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def lcs_string(s1: str, s2: str) -> str:
    """Reconstruct the actual LCS string by backtracking through the DP table."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # Backtrack to find the sequence
    result = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            result.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return ''.join(reversed(result))
```

## Longest Increasing Subsequence

```python
import bisect

def lis_length(nums: list[int]) -> int:
    """Length of longest increasing subsequence. O(n log n) time, O(n) space.

    Uses patience sorting: maintain a list of smallest tail elements.
    For each number, replace the first tail >= num, or append if larger than all.
    The length of this list equals the LIS length.
    """
    tails: list[int] = []
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)
```

## Edit Distance (Levenshtein)

```python
def edit_distance(s1: str, s2: str) -> int:
    """Minimum edit operations (insert, delete, replace) to transform s1 into s2.
    O(mn) time, O(mn) space.
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete from s1
                    dp[i][j - 1],      # insert into s1
                    dp[i - 1][j - 1],  # replace in s1
                )
    return dp[m][n]


def edit_distance_optimized(s1: str, s2: str) -> int:
    """Space-optimized edit distance. O(mn) time, O(n) space."""
    m, n = len(s1), len(s2)
    prev = list(range(n + 1))
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev
    return prev[n]
```

## Matrix Chain Multiplication

```python
def matrix_chain_order(dims: list[int]) -> int:
    """Minimum scalar multiplications to multiply chain of matrices.
    dims[i-1] x dims[i] gives dimensions of matrix i.
    O(n^3) time, O(n^2) space.
    """
    n = len(dims) - 1  # number of matrices
    dp = [[0] * n for _ in range(n)]
    # l is chain length
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                dp[i][j] = min(dp[i][j], cost)
    return dp[0][n - 1]
```

## General Tips

When the DP state involves only the previous row or previous few values, apply space optimization by keeping only those rows in memory. This reduces space from O(n*m) to O(m) or even O(1) for single-variable recurrences like Fibonacci.

For problems with large state spaces, consider whether the state can be compressed. Bitmask DP uses an integer to represent a subset of items, enabling states like `dp[mask]` where `mask` is a bitmask of visited nodes. This is practical when n <= 20 or so, since 2^20 is about one million states.

Always verify base cases carefully. Off-by-one errors in DP are extremely common. A good practice is to trace through the first few iterations manually before running the code.
