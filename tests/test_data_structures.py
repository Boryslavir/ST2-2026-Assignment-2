import pytest


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



def test_bst_inorder():
    root = None
    for v in [5, 3, 7, 2, 4, 6, 8]:
        root = insert(root, v)
    assert inorder(root) == "2 3 4 5 6 7 8 "

def test_bst_preorder():
    root = None
    for v in [5, 3, 7]:
        root = insert(root, v)
    assert preorder(root) == "5 3 7 "

def test_bst_postorder():
    root = None
    for v in [5, 3, 7]:
        root = insert(root, v)
    assert postorder(root) == "3 7 5 "


def test_linked_list_insert():
    ll = []
    ll.append(10)
    ll.append(20)
    assert ll == [10, 20]

def test_linked_list_delete():
    ll = [10, 20, 30]
    ll.remove(20)
    assert ll == [10, 30]

def test_linked_list_reverse():
    ll = [1, 2, 3]
    ll.reverse()
    assert ll == [3, 2, 1]


def test_queue_enqueue():
    q = []
    q.append(5)
    q.append(10)
    assert q == [5, 10]

def test_queue_dequeue():
    q = [5, 10, 15]
    q.pop(0)
    assert q == [10, 15]


def test_stack_push():
    s = []
    s.append(7)
    s.append(9)
    assert s == [7, 9]

def test_stack_pop():
    s = [1, 2, 3]
    s.pop()
    assert s == [1, 2]
