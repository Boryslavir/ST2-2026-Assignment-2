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


from modules.heap import HeapModule


def is_min_heap(data: list[int]) -> bool:
    """Return True if `data` satisfies the min-heap property."""
    n = len(data)
    for i in range(n):
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and data[l] < data[i]:
            return False
        if r < n and data[r] < data[i]:
            return False
    return True


def fresh_module(preload: list[int] | None = None) -> HeapModule:
    """
    Return a HeapModule with a known, controllable initial state.
    Pass preload=[] to start with an empty heap.
    """
    mod = HeapModule()
    mod._do_reset()                        # clear the default PRELOAD values
    if preload:
        for v in preload:
            mod._heap_insert(v)
    return mod


class TestHeapInsert(unittest.TestCase):
    """Heap insertion preserves the min-heap property after every insert."""

    def test_single_insert(self):
        mod = fresh_module()
        mod._animate_insert(10)
        self.assertEqual(mod.data, [10])


    def test_min_heap_property_after_each_insert(self):
        """After every insert the heap invariant must hold."""
        mod = fresh_module()
        for val in [40, 70, 30, 90, 50, 20, 60]:
            mod._animate_insert(val)
            self.assertTrue(
                is_min_heap(mod.data),
                f"Heap property violated after inserting {val}: {mod.data}"
            )


    def test_root_is_always_minimum(self):
        values = [40, 70, 30, 90, 50, 20, 60]
        mod = fresh_module()
        for val in values:
            mod._animate_insert(val)
        self.assertEqual(mod.data[0], min(values))


    def test_size_grows_correctly(self):
        mod = fresh_module()
        for i, val in enumerate([5, 3, 8, 1, 2], start=1):
            mod._animate_insert(val)
            self.assertEqual(len(mod.data), i)


    def test_insert_status_message(self):
        mod = fresh_module()
        mod._animate_insert(42)
        self.assertIn("42", mod.status_msg)
        self.assertIn("1", mod.status_msg)   # heap size


    def test_highlight_cleared_after_insert(self):
        """Animation highlight must be empty once insertion completes."""
        mod = fresh_module()
        mod._animate_insert(10)
        mod._animate_insert(5)   # triggers a sift-up swap
        self.assertEqual(mod.highlight, set())


    def test_duplicate_values(self):
        mod = fresh_module()
        for val in [5, 5, 5]:
            mod._animate_insert(val)
        self.assertTrue(is_min_heap(mod.data))
        self.assertEqual(len(mod.data), 3)


class TestHeapExtract(unittest.TestCase):
    """Extract-min always removes the smallest element and re-heapifies."""

    def test_extract_returns_minimum(self):
        values = [40, 70, 30, 90, 50, 20, 60]
        mod = fresh_module(preload=values)
        before_min = min(mod.data)
        mod._animate_extract()
        self.assertIn(str(before_min), mod.status_msg)


    def test_heap_property_after_extract(self):
        mod = fresh_module(preload=[40, 70, 30, 90, 50, 20, 60])
        mod._animate_extract()
        self.assertTrue(is_min_heap(mod.data))


    def test_size_shrinks_by_one(self):
        mod = fresh_module(preload=[10, 20, 30])
        size_before = len(mod.data)
        mod._animate_extract()
        self.assertEqual(len(mod.data), size_before - 1)


    def test_sequential_extracts_give_sorted_order(self):
        """Repeatedly extracting from the heap yields ascending sorted order."""
        values = [40, 70, 30, 90, 50, 20, 60]
        mod = fresh_module(preload=values)
        extracted: list[int] = []
        while mod.data:
            root = mod.data[0]
            mod._animate_extract()
            extracted.append(root)
        self.assertEqual(extracted, sorted(values))


    def test_extract_from_single_element(self):
        mod = fresh_module(preload=[99])
        mod._animate_extract()
        self.assertEqual(mod.data, [])
        self.assertIn("empty", mod.status_msg.lower())


    def test_extract_from_empty_heap(self):
        mod = fresh_module()
        mod._animate_extract()   # must not raise
        self.assertIn("empty", mod.status_msg.lower())


    def test_highlight_cleared_after_extract(self):
        mod = fresh_module(preload=[40, 70, 30])
        mod._animate_extract()
        self.assertEqual(mod.highlight, set())


    def test_heap_property_maintained_across_multiple_extracts(self):
        mod = fresh_module(preload=[5, 9, 3, 7, 1, 8, 2])
        for _ in range(4):
            mod._animate_extract()
            if mod.data:
                self.assertTrue(is_min_heap(mod.data))


class TestHeapReset(unittest.TestCase):
    """_do_reset clears all mutable state."""

    def test_reset_empties_data(self):
        mod = fresh_module(preload=[10, 20, 30])
        mod._do_reset()
        self.assertEqual(mod.data, [])


    def test_reset_clears_highlight(self):
        mod = fresh_module(preload=[10, 5])
        mod.highlight = {0, 1}
        mod._do_reset()
        self.assertEqual(mod.highlight, set())


    def test_reset_clears_input_buffer(self):
        mod = fresh_module()
        mod.input_buf = "123"
        mod._do_reset()
        self.assertEqual(mod.input_buf, "")


class TestHeapSilentVsAnimatedInsert(unittest.TestCase):
    """Silent (_heap_insert) and animated (_animate_insert) must produce identical heaps."""

    def test_identical_heap_structure(self):
        values = [40, 70, 30, 90, 50, 20, 60]

        silent_mod = fresh_module()
        for v in values:
            silent_mod._heap_insert(v)

        animated_mod = fresh_module()
        for v in values:
            animated_mod._animate_insert(v)

        self.assertEqual(silent_mod.data, animated_mod.data)


    def test_preload_satisfies_heap_property(self):
        """The default PRELOAD values result in a valid min-heap."""
        mod = HeapModule()   # uses PRELOAD via __init__
        self.assertTrue(is_min_heap(mod.data))


    def test_preload_root_is_minimum(self):
        mod = HeapModule()
        self.assertEqual(mod.data[0], min(HeapModule.PRELOAD))


class TestNodePosition(unittest.TestCase):
    """_node_pos must return sensible screen coordinates for tree layout."""

    def test_root_is_centred(self):
        from cores.globals import WIDTH
        mod = HeapModule()
        x, y = mod._node_pos(0)
        self.assertEqual(x, WIDTH // 2)


    def test_children_below_parent(self):
        mod = HeapModule()
        _, y_root    = mod._node_pos(0)
        _, y_child_l = mod._node_pos(1)
        _, y_child_r = mod._node_pos(2)
        self.assertGreater(y_child_l, y_root)
        self.assertGreater(y_child_r, y_root)


    def test_grandchildren_below_children(self):
        mod = HeapModule()
        _, y_child       = mod._node_pos(1)
        _, y_grandchild  = mod._node_pos(3)
        self.assertGreater(y_grandchild, y_child)


if __name__ == "__main__":
    unittest.main()
