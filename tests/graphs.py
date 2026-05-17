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


from modules.graphs import GraphModule


def run_traversal(start: str, algo: str) -> list[str]:
    """
    Run a full BFS or DFS from `start` and return the list of nodes
    in the order they were first visited (NODE_CURRENT state).
    """
    mod = GraphModule()
    mod.start_node = start
    mod._start_algo(algo)

    visit_order: list[str] = []
    for status in mod.gen:
        # "Visiting X" is emitted exactly once per node when it becomes current
        if status.startswith("Visiting "):
            node = status.split()[-1]
            visit_order.append(node)

    return visit_order


def bfs_expected(graph: dict[str, list[str]], start: str) -> list[str]:
    """Reference BFS (neighbours sorted alphabetically, matching GraphModule)."""
    from collections import deque
    visited: set[str]  = set()
    order:   list[str] = []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for nb in sorted(graph[node]):
            if nb not in visited:
                queue.append(nb)
    return order


def dfs_expected(graph: dict[str, list[str]], start: str) -> list[str]:
    """Reference DFS (neighbours pushed in reverse-sorted order, matching GraphModule)."""
    visited: set[str]  = set()
    order:   list[str] = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for nb in sorted(graph[node], reverse=True):
            if nb not in visited:
                stack.append(nb)
    return order


# Build the adjacency list from GraphModule's class-level constants
def _build_adj() -> dict[str, list[str]]:
    mod = GraphModule()
    return mod.adj


class TestBFSFromA(unittest.TestCase):
    """BFS traversal from A — nodes visited in correct BFS order"""

    def setUp(self):
        self.adj = _build_adj()


    def test_visit_order_matches_bfs(self):
        """Actual visit order equals the reference BFS order from A."""
        actual   = run_traversal('A', "BFS")
        expected = bfs_expected(self.adj, 'A')
        self.assertEqual(actual, expected)


    def test_all_nodes_visited(self):
        """Every node in the graph is reached from A (graph is connected)."""
        actual = run_traversal('A', "BFS")
        self.assertEqual(sorted(actual), sorted(GraphModule.NODES.keys()))


    def test_start_node_is_first(self):
        """The start node must be the first node visited."""
        actual = run_traversal('A', "BFS")
        self.assertEqual(actual[0], 'A')


    def test_no_duplicate_visits(self):
        """Each node appears exactly once in the visit order."""
        actual = run_traversal('A', "BFS")
        self.assertEqual(len(actual), len(set(actual)))


    def test_completion_status(self):
        """Generator ends with 'BFS complete!' message."""
        mod = GraphModule()
        mod.start_node = 'A'
        mod._start_algo("BFS")
        last_status = None
        for status in mod.gen:
            last_status = status
        self.assertEqual(last_status, "BFS complete!")


class TestDFSFromC(unittest.TestCase):
    """DFS traversal from C — traversal path matches theoretical DFS"""

    def setUp(self):
        self.adj = _build_adj()


    def test_visit_order_matches_dfs(self):
        """Actual visit order equals the reference DFS order from C."""
        actual   = run_traversal('C', "DFS")
        expected = dfs_expected(self.adj, 'C')
        self.assertEqual(actual, expected)


    def test_all_nodes_visited(self):
        """Every node is reachable from C."""
        actual = run_traversal('C', "DFS")
        self.assertEqual(sorted(actual), sorted(GraphModule.NODES.keys()))


    def test_start_node_is_first(self):
        actual = run_traversal('C', "DFS")
        self.assertEqual(actual[0], 'C')


    def test_no_duplicate_visits(self):
        actual = run_traversal('C', "DFS")
        self.assertEqual(len(actual), len(set(actual)))


    def test_completion_status(self):
        mod = GraphModule()
        mod.start_node = 'C'
        mod._start_algo("DFS")
        last_status = None
        for status in mod.gen:
            last_status = status
        self.assertEqual(last_status, "DFS complete!")


class TestInteractiveStartNode(unittest.TestCase):
    """Interactive start node — BFS restarts correctly from chosen node"""

    def test_bfs_from_each_node_starts_correctly(self):
        """
        Simulate clicking every node as start: BFS from each must begin
        at that node and visit all others exactly once.
        """
        adj = _build_adj()
        for start in GraphModule.NODES:
            with self.subTest(start=start):
                actual   = run_traversal(start, "BFS")
                expected = bfs_expected(adj, start)
                self.assertEqual(actual, expected, f"BFS from {start} incorrect")


    def test_start_node_change_resets_colours(self):
        """After changing start node, all node colours return to NODE_DEFAULT."""
        from cores.globals import NODE_DEFAULT
        mod = GraphModule()
        mod._start_algo("BFS")
        # exhaust it so colours change
        for _ in mod.gen:
            pass
        # simulate clicking a new start node
        mod.start_node = 'E'
        mod._reset_colours()
        for colour in mod.node_colours.values():
            self.assertEqual(colour, NODE_DEFAULT)


    def test_dfs_from_each_node_starts_correctly(self):
        """DFS from every possible start node produces the correct order."""
        adj = _build_adj()
        for start in GraphModule.NODES:
            with self.subTest(start=start):
                actual   = run_traversal(start, "DFS")
                expected = dfs_expected(adj, start)
                self.assertEqual(actual, expected, f"DFS from {start} incorrect")


    def test_bfs_then_reset_then_bfs_from_new_start(self):
        """
        Running BFS, resetting, changing start, and running BFS again
        produces the correct result for the new start node.
        """
        adj = _build_adj()
        mod = GraphModule()
        mod.start_node = 'A'
        mod._start_algo("BFS")
        for _ in mod.gen:
            pass

        # Reset and change start
        mod._do_reset()
        mod.start_node = 'G'
        mod._start_algo("BFS")

        visit_order: list[str] = []
        for status in mod.gen:
            if status.startswith("Visiting "):
                visit_order.append(status.split()[-1])

        self.assertEqual(visit_order, bfs_expected(adj, 'G'))


class TestGraphModuleAdjacency(unittest.TestCase):
    """Sanity-checks on the graph structure used by all traversals."""

    def test_graph_is_undirected(self):
        """Every edge (u, v) has v in adj[u] and u in adj[v]."""
        mod = GraphModule()
        for u, v in GraphModule.EDGES:
            self.assertIn(v, mod.adj[u], f"Missing {u}→{v}")
            self.assertIn(u, mod.adj[v], f"Missing {v}→{u}")

    def test_all_nodes_have_adjacency_entry(self):
        mod = GraphModule()
        for node in GraphModule.NODES:
            self.assertIn(node, mod.adj)

    def test_node_count(self):
        self.assertEqual(len(GraphModule.NODES), 8)


if __name__ == "__main__":
    unittest.main()
