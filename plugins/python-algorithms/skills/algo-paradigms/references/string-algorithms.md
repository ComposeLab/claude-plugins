# String Algorithms

String algorithms deal with pattern matching, text comparison, and structural analysis of sequences. Many string problems have naive O(n*m) solutions that can be improved to O(n+m) with preprocessing. This reference covers the essential algorithms with complete Python implementations and guidance on when to use built-in methods versus custom implementations.

## When to Use Built-in Methods vs Custom Algorithms

Python's built-in string methods and the `re` module handle most practical string tasks efficiently. Use `str.find()`, `str.count()`, or `in` for simple substring search -- CPython uses a hybrid Boyer-Moore/Horspool algorithm internally, which is highly optimized in C. Use the `re` module for pattern matching with wildcards, character classes, or repetition.

Custom algorithmic implementations become necessary when: you need to understand the time complexity guarantees (interviews, competitive programming), the problem requires modifications to standard algorithms (weighted edit distance, approximate matching), you are processing very large texts where constant factors matter and you need control over the algorithm, or the problem is a DP variant on strings (edit distance, LCS) that does not map to regex.

## KMP (Knuth-Morris-Pratt) Pattern Matching

KMP achieves O(n + m) pattern matching by preprocessing the pattern to build a failure function (also called the prefix function or partial match table). The failure function tells you, for each position in the pattern, the length of the longest proper prefix that is also a suffix. This allows the algorithm to skip characters in the text that have already been matched, avoiding the backtracking that makes naive matching O(n*m).

The failure function works because when a mismatch occurs at pattern position j, the characters pattern[0..j-1] have already matched the text. The failure function tells us the longest prefix of the pattern that is also a suffix of the matched portion, so we can continue matching from that prefix instead of starting over.

```python
def kmp_build_failure(pattern: str) -> list[int]:
    """Build the KMP failure function for the pattern.
    failure[i] = length of longest proper prefix of pattern[0..i]
    that is also a suffix. O(m) time.
    """
    m = len(pattern)
    failure = [0] * m
    length = 0  # length of previous longest prefix-suffix
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            failure[i] = length
            i += 1
        elif length != 0:
            length = failure[length - 1]
            # do not increment i
        else:
            failure[i] = 0
            i += 1
    return failure


def kmp_search(text: str, pattern: str) -> list[int]:
    """Find all occurrences of pattern in text using KMP.
    Returns list of starting indices. O(n + m) time.
    """
    if not pattern:
        return list(range(len(text) + 1))
    n, m = len(text), len(pattern)
    failure = kmp_build_failure(pattern)
    matches: list[int] = []
    j = 0  # position in pattern
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = failure[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            matches.append(i - m + 1)
            j = failure[j - 1]
    return matches
```

## Rabin-Karp (Rolling Hash)

Rabin-Karp uses hashing to find pattern matches. It computes a hash for the pattern and a rolling hash for each window of the text. When hashes match, it verifies with a character-by-character comparison to handle collisions. The expected time is O(n + m), though worst case is O(n*m) due to hash collisions.

Rabin-Karp shines when searching for multiple patterns simultaneously (compute hashes for all patterns and check each window against a set of hashes) or when the problem involves finding duplicate substrings.

```python
def rabin_karp_search(text: str, pattern: str, base: int = 256, mod: int = 10**9 + 7) -> list[int]:
    """Find all occurrences of pattern in text using Rabin-Karp.
    Expected O(n + m) time. Uses rolling hash with given base and modulus.
    """
    n, m = len(text), len(pattern)
    if m > n:
        return []

    # Compute hash of pattern and first window
    pat_hash = 0
    win_hash = 0
    highest_pow = pow(base, m - 1, mod)

    for i in range(m):
        pat_hash = (pat_hash * base + ord(pattern[i])) % mod
        win_hash = (win_hash * base + ord(text[i])) % mod

    matches: list[int] = []
    for i in range(n - m + 1):
        if win_hash == pat_hash:
            # Verify to handle hash collisions
            if text[i:i + m] == pattern:
                matches.append(i)
        # Slide the window: remove leftmost char, add next char
        if i < n - m:
            win_hash = (win_hash - ord(text[i]) * highest_pow) % mod
            win_hash = (win_hash * base + ord(text[i + m])) % mod
            win_hash = (win_hash + mod) % mod  # ensure non-negative

    return matches
```

## Edit Distance (Levenshtein Distance)

Edit distance measures the minimum number of single-character operations (insert, delete, replace) to transform one string into another. This is a classic DP problem on two strings. The state `dp[i][j]` represents the edit distance between the first `i` characters of s1 and the first `j` characters of s2.

The recurrence captures three operations: if the current characters match, no operation is needed and `dp[i][j] = dp[i-1][j-1]`. Otherwise, take the minimum of delete (`dp[i-1][j] + 1`), insert (`dp[i][j-1] + 1`), or replace (`dp[i-1][j-1] + 1`).

```python
def edit_distance(s1: str, s2: str) -> int:
    """Minimum edit operations to transform s1 into s2.
    O(mn) time, O(n) space with rolling array optimization.
    """
    m, n = len(s1), len(s2)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        curr = [i] + [0] * n
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[n]


def edit_distance_with_ops(s1: str, s2: str) -> tuple[int, list[str]]:
    """Edit distance with operation reconstruction.
    Returns (distance, list of operation descriptions).
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
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    # Backtrack to find operations
    ops: list[str] = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            ops.append(f"Replace '{s1[i-1]}' at position {i-1} with '{s2[j-1]}'")
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            ops.append(f"Insert '{s2[j-1]}' at position {i}")
            j -= 1
        else:
            ops.append(f"Delete '{s1[i-1]}' at position {i-1}")
            i -= 1
    return dp[m][n], list(reversed(ops))
```

## Longest Common Subsequence

LCS finds the longest sequence of characters that appears in both strings in order (not necessarily contiguous). This is closely related to edit distance: the edit distance between two strings equals `len(s1) + len(s2) - 2 * lcs(s1, s2)` when only insert and delete operations are allowed.

```python
def lcs(s1: str, s2: str) -> str:
    """Find the longest common subsequence string. O(mn) time and space."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # Reconstruct
    result: list[str] = []
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

## Longest Palindromic Substring

Finding the longest palindromic substring can be done with DP in O(n^2) time and space, or with the expand-around-center approach in O(n^2) time and O(1) space. The expand-around-center approach is simpler and more space-efficient: for each possible center (including centers between characters for even-length palindromes), expand outward while characters match.

```python
def longest_palindrome_substring(s: str) -> str:
    """Find the longest palindromic substring. O(n^2) time, O(1) space.
    Uses expand-around-center approach.
    """
    if len(s) < 2:
        return s
    start, max_len = 0, 1

    def expand(left: int, right: int) -> tuple[int, int]:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - left - 1

    for i in range(len(s)):
        # Odd-length palindromes centered at i
        lo, length = expand(i, i)
        if length > max_len:
            start, max_len = lo, length
        # Even-length palindromes centered between i and i+1
        lo, length = expand(i, i + 1)
        if length > max_len:
            start, max_len = lo, length

    return s[start:start + max_len]
```

## String Hashing

String hashing converts a string to a numeric value, enabling O(1) substring comparison after O(n) preprocessing. This is the foundation of Rabin-Karp and is useful for problems involving duplicate substring detection, longest repeated substring, and string comparison in hash maps.

```python
class StringHasher:
    """Polynomial rolling hash for O(1) substring hash queries.
    After O(n) preprocessing, any substring hash can be computed in O(1).
    """
    def __init__(self, s: str, base: int = 31, mod: int = 10**9 + 9):
        self.mod = mod
        self.base = base
        n = len(s)
        self.prefix_hash = [0] * (n + 1)
        self.power = [1] * (n + 1)
        for i in range(n):
            self.prefix_hash[i + 1] = (
                self.prefix_hash[i] * base + ord(s[i]) - ord('a') + 1
            ) % mod
            self.power[i + 1] = (self.power[i] * base) % mod

    def get_hash(self, left: int, right: int) -> int:
        """Hash of s[left:right+1] in O(1)."""
        raw = (
            self.prefix_hash[right + 1]
            - self.prefix_hash[left] * self.power[right - left + 1]
        ) % self.mod
        return (raw + self.mod) % self.mod
```

## Practical Guidance

For interview and competitive programming contexts, KMP and edit distance are the most commonly tested string algorithms. KMP demonstrates understanding of preprocessing for efficiency, while edit distance demonstrates DP on two sequences.

For production code, prefer Python's built-in `str.find()` and `re` module. They are implemented in C, heavily optimized, and handle edge cases that custom implementations might miss (Unicode, empty strings, etc.). Reserve custom implementations for when you need algorithmic guarantees or problem-specific modifications.
