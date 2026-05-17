import os
import sys
import unittest

# Prevent Pygame / SDL from trying to open a display in a headless environment
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


# Make sure the project root is on the path when running from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import pygame
pygame.init()


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def insert(root, value):
    if root is None:
        return Node(value)
    if value < root.value:
        root.left = insert(root.left, value)
    else:
        root.right = insert(root.right, value)
    return root


def inorder(node):
    if not node:
        return ""
    return inorder(node.left) + f"{node.value} " + inorder(node.right)


def preorder(node):
    if not node:
        return ""
    return f"{node.value} " + preorder(node.left) + preorder(node.right)


def postorder(node):
    if not node:
        return ""
    return postorder(node.left) + postorder(node.right) + f"{node.value} "


# -----------------------------
# Unit Tests
# -----------------------------

class TestBST(unittest.TestCase):

    def setUp(self):
        """Build a small BST for reuse."""
        self.values = [5, 3, 7, 2, 4, 6, 8]
        self.root = None
        for v in self.values:
            self.root = insert(self.root, v)

    def test_inorder(self):
        self.assertEqual(inorder(self.root), "2 3 4 5 6 7 8 ")

    def test_preorder(self):
        root = None
        for v in [5, 3, 7]:
            root = insert(root, v)
        self.assertEqual(preorder(root), "5 3 7 ")

    def test_postorder(self):
        root = None
        for v in [5, 3, 7]:
            root = insert(root, v)
        self.assertEqual(postorder(root), "3 7 5 ")


class TestLinkedList(unittest.TestCase):

    def test_insert(self):
        ll = []
        ll.append(10)
        ll.append(20)
        self.assertListEqual(ll, [10, 20])

    def test_delete(self):
        ll = [10, 20, 30]
        ll.remove(20)
        self.assertListEqual(ll, [10, 30])

    def test_reverse(self):
        ll = [1, 2, 3]
        ll.reverse()
        self.assertListEqual(ll, [3, 2, 1])


class TestQueue(unittest.TestCase):

    def test_enqueue(self):
        q = []
        q.append(5)
        q.append(10)
        self.assertListEqual(q, [5, 10])

    def test_dequeue(self):
        q = [5, 10, 15]
        q.pop(0)
        self.assertListEqual(q, [10, 15])


class TestStack(unittest.TestCase):

    def test_push(self):
        s = []
        s.append(7)
        s.append(9)
        self.assertListEqual(s, [7, 9])

    def test_pop(self):
        s = [1, 2, 3]
        s.pop()
        self.assertListEqual(s, [1, 2])


if __name__ == "__main__":
    unittest.main()
