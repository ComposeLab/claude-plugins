"""Binary Search Tree implementation with insert and search operations."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class TreeNode:
    """A single node in the binary search tree."""
    val: Any
    left: TreeNode | None = None
    right: TreeNode | None = None


class BST:
    """Binary Search Tree with insert and search operations.

    The BST invariant: for every node, all values in its left subtree
    are smaller, and all values in its right subtree are larger.

    This invariant enables O(h) search and insert, where h is the tree height.
    - Best case: h = O(log n) when the tree is balanced
    - Worst case: h = O(n) when the tree degenerates into a linked list
    """

    def __init__(self) -> None:
        """Initialize an empty binary search tree."""
        self.root: TreeNode | None = None

    def insert(self, val: Any) -> None:
        """Insert a value into the BST, maintaining the BST property.

        Args:
            val: The value to insert.

        Time Complexity: O(h) where h is tree height
        Space Complexity: O(h) for recursion stack
        """
        self.root = self._insert(self.root, val)

    def _insert(self, node: TreeNode | None, val: Any) -> TreeNode:
        """Recursively insert a value into the subtree rooted at node.

        Args:
            node: Current node (None if subtree is empty)
            val: Value to insert

        Returns:
            The root of the subtree after insertion
        """
        if node is None:
            return TreeNode(val)

        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        # If val == node.val, we ignore duplicates and just return the node

        return node

    def search(self, val: Any) -> bool:
        """Search for a value in the BST.

        Args:
            val: The value to search for.

        Returns:
            True if the value exists in the tree, False otherwise.

        Time Complexity: O(h) where h is tree height
        Space Complexity: O(h) for recursion stack
        """
        return self._search(self.root, val)

    def _search(self, node: TreeNode | None, val: Any) -> bool:
        """Recursively search for a value in the subtree rooted at node.

        Args:
            node: Current node (None if subtree is empty)
            val: Value to search for

        Returns:
            True if value is found, False otherwise
        """
        if node is None:
            return False

        if val == node.val:
            return True

        if val < node.val:
            return self._search(node.left, val)
        else:
            return self._search(node.right, val)

    def search_iterative(self, val: Any) -> bool:
        """Search for a value in the BST using iteration (non-recursive).

        This approach avoids recursion depth limitations and is often more
        efficient in practice due to better cache locality.

        Args:
            val: The value to search for.

        Returns:
            True if the value exists in the tree, False otherwise.

        Time Complexity: O(h) where h is tree height
        Space Complexity: O(1) - no recursion stack
        """
        node = self.root

        while node is not None:
            if val == node.val:
                return True
            elif val < node.val:
                node = node.left
            else:
                node = node.right

        return False

    def inorder_traversal(self) -> list[Any]:
        """Return nodes in sorted order via inorder traversal.

        Inorder traversal on a BST yields values in ascending order.
        This is useful for verifying BST correctness or getting sorted output.

        Time Complexity: O(n)
        Space Complexity: O(h) for recursion stack
        """
        result: list[Any] = []

        def _traverse(node: TreeNode | None) -> None:
            if node is None:
                return
            _traverse(node.left)
            result.append(node.val)
            _traverse(node.right)

        _traverse(self.root)
        return result


# Example usage and test cases
if __name__ == "__main__":
    # Create a BST and insert values
    bst = BST()
    values = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 65]

    print("Inserting values:", values)
    for val in values:
        bst.insert(val)

    print("\nInorder traversal (sorted):", bst.inorder_traversal())

    # Test search operations
    print("\n--- Testing Search ---")
    search_values = [20, 50, 100, 65, 15]
    for val in search_values:
        recursive_result = bst.search(val)
        iterative_result = bst.search_iterative(val)
        print(f"Search for {val}: Recursive={recursive_result}, Iterative={iterative_result}")

    # Demonstrate balanced vs unbalanced tree
    print("\n--- Balanced Tree ---")
    balanced_bst = BST()
    balanced_values = [50, 30, 70, 20, 40, 60, 80]
    for val in balanced_values:
        balanced_bst.insert(val)
    print("Balanced tree inorder:", balanced_bst.inorder_traversal())
    print("Search for 20:", balanced_bst.search(20))

    print("\n--- Degenerate Tree (linked list) ---")
    degenerate_bst = BST()
    degenerate_values = [1, 2, 3, 4, 5]
    for val in degenerate_values:
        degenerate_bst.insert(val)
    print("Degenerate tree inorder:", degenerate_bst.inorder_traversal())
    print("Search for 3:", degenerate_bst.search(3))
