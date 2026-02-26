# Paradigm Selection

Choosing the right algorithmic paradigm is the most consequential decision when solving a problem. A greedy approach on a problem that requires DP will produce wrong answers, while using DP on a problem amenable to greedy wastes time and space. This reference provides a framework for recognizing which paradigm fits.

## The Four Paradigms at a Glance

| Paradigm | Key Property | Typical Signal | Time Trade-off |
|---|---|---|---|
| Dynamic Programming | Overlapping subproblems + optimal substructure | "Find the minimum/maximum/count of ways" | Polynomial (often O(n^2) or O(n*W)) |
| Greedy | Greedy choice property + optimal substructure | "Find the maximum number of non-overlapping items" | Often O(n log n) due to sorting |
| Backtracking | Constraint satisfaction or enumeration | "Find all configurations" or "is there a valid assignment" | Exponential worst-case, pruning helps |
| String Algorithms | Pattern or text structure | "Find occurrences", "match pattern", "edit distance" | O(n + m) to O(n*m) depending on problem |

## Recognizing Dynamic Programming Problems

DP applies when a problem has two properties simultaneously. First, optimal substructure means the optimal solution to the whole problem can be composed from optimal solutions to subproblems. Second, overlapping subproblems means the same subproblems are solved multiple times in a naive recursive approach.

The classic signal is a problem asking for an optimum (minimum cost, maximum profit, number of ways) over a sequence or grid where choices at each step depend on previous choices. If you write a recursive solution and notice the same arguments appearing in multiple recursive calls, DP is the right paradigm.

Common DP problem patterns include:
- Sequence optimization: longest increasing subsequence, longest common subsequence
- Counting paths: grid traversal, staircase problems, coin change count
- Subset optimization: 0/1 knapsack, partition equal subset sum
- String comparison: edit distance, regex matching, interleaving strings

## Recognizing Greedy Problems

Greedy algorithms work when making the locally optimal choice at each step leads to the globally optimal solution. This requires the greedy choice property: a globally optimal solution can be arrived at by making a locally optimal (greedy) choice. Unlike DP, you never need to reconsider previous choices.

The signal for greedy is often a problem involving scheduling, selection, or ordering where sorting by some criterion and then iterating once produces the answer. If the problem asks "what is the maximum number of non-overlapping intervals" or "what is the minimum number of coins (with canonical denominations)", greedy likely works.

Common greedy problem patterns include:
- Interval scheduling: activity selection, meeting rooms
- Huffman-style encoding: frequency-based merging
- Fractional optimization: fractional knapsack (items can be split)
- Graph algorithms: Dijkstra, Prim, Kruskal (greedy on edges/distances)

## Recognizing Backtracking Problems

Backtracking is the paradigm of choice when you need to explore a search space systematically, either to find all valid configurations or to find any one valid configuration. The search space is typically exponential, but pruning (cutting off branches that cannot lead to valid solutions) makes it practical.

The signal is a problem asking you to generate all combinations, permutations, or valid arrangements subject to constraints. If the problem says "find all subsets that sum to X" or "place N queens on a board such that none attack each other", backtracking is the paradigm.

Common backtracking problem patterns include:
- Combinatorial generation: permutations, combinations, subsets, power set
- Constraint satisfaction: N-Queens, Sudoku, crossword puzzles
- Path finding with constraints: maze solving, word search in grid
- Partition problems: partition into k equal-sum subsets

## When Greedy Fails and DP Is Needed

This is the most common misidentification. A problem may look greedy at first glance but require DP. The telltale sign is that a greedy choice can be locally optimal but lead to a globally suboptimal result.

The classic example is the 0/1 knapsack. A greedy approach of picking items by highest value-to-weight ratio fails because you cannot take fractions of items. Consider items with weights [2, 3, 4] and values [3, 4, 5] with capacity 5. Greedy by ratio picks the first item (ratio 1.5) then the second (ratio 1.33), total value 7 at weight 5. But picking items 2 and 3 is not possible (weight 7). Actually picking item 1 (w=2, v=3) and item 2 (w=3, v=4) gives value 7 and weight 5, which matches. A better counter-example: weights [1, 3, 4, 5], values [1, 4, 5, 7], capacity 7. Greedy by ratio picks item 1 (ratio 1.0), item 2 (ratio 1.33), total w=4, v=5, then item 3 does not fit (w=4+4=8), item 4 does not fit. So greedy gets 5. But items 2+3 (w=3+4=7, v=4+5=9) gives 9, which is better.

Another example is the coin change problem with non-canonical denominations. With coins [1, 3, 4] and target 6, greedy picks 4+1+1=3 coins, but 3+3=2 coins is optimal.

When in doubt, try to construct a counterexample for the greedy approach. If you can find one, use DP instead.

## Decision Flowchart Approach

Follow these questions in order:

1. Does the problem ask to find/count/enumerate ALL valid configurations? If yes, use backtracking (possibly with memoization if subproblems overlap).

2. Does the problem involve string pattern matching or text processing? If yes, consult string algorithms first. Some string problems (edit distance, LCS) are DP problems.

3. Does the problem ask for an optimum and have overlapping subproblems? Write a few levels of the recursion tree. If subproblems repeat, use DP.

4. Can you prove that a local optimal choice always leads to a global optimum? If yes, use greedy. If you cannot prove it or find a counterexample, fall back to DP.

5. If the search space is small enough (constraints suggest n <= 20 or so), backtracking with pruning may suffice even for optimization problems.

## Real-World Problem Mapping

| Problem | Paradigm | Reason |
|---|---|---|
| Shortest path in weighted graph | Greedy (Dijkstra) or DP (Bellman-Ford) | Non-negative weights allow greedy; negative weights need DP |
| Minimum edit operations between strings | DP | Overlapping subproblems in prefix comparisons |
| Schedule maximum non-overlapping meetings | Greedy | Sort by end time, always pick earliest-ending |
| Generate all valid parentheses combinations | Backtracking | Enumerate with constraint pruning |
| Find longest palindromic substring | DP or String (Manacher) | Expand-around-center or DP on substrings |
| Minimum coins to make change | DP (usually) | Greedy fails for non-canonical denominations |
| Assign tasks to minimize total cost | DP (bitmask) or Backtracking | Hungarian algorithm or bitmask DP for small n |
| Find all subsets summing to target | Backtracking | Enumerate subsets with pruning |
