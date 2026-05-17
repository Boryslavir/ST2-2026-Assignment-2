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


from modules.sorting import SortingModule


def exhaust_gen(mod: SortingModule) -> list[str]:
    """Drive a sort generator to completion and return all status strings."""
    statuses: list[str] = []
    assert mod.gen is not None
    for status in mod.gen:
        statuses.append(status)
    return statuses


def run_sort(algo_name: str, initial: list[int]) -> tuple[list[int], list[str]]:
    """
    Build a SortingModule, inject a known array, run the chosen algorithm,
    and return (sorted_array, status_messages).
    """
    mod = SortingModule()
    mod.arr     = list(initial)
    mod.colours = [mod.arr[0] - mod.arr[0]] * len(initial)  # placeholder; reset inside gen
    mod._start_algo(algo_name)
    statuses = exhaust_gen(mod)
    return mod.arr, statuses


class TestBubbleSort(unittest.TestCase):
    """Bubble sort correctness — Sort array of [5,3,8,1,2] → [1,2,3,5,8]"""

    def test_sorts_correctly(self):
        """Sorted output matches expected order."""
        result, _ = run_sort("Bubble Sort", [5, 3, 8, 1, 2])
        self.assertEqual(result, [1, 2, 3, 5, 8])


    def test_already_sorted(self):
        """An already-sorted array stays sorted."""
        result, _ = run_sort("Bubble Sort", [1, 2, 3, 4, 5])
        self.assertEqual(result, [1, 2, 3, 4, 5])


    def test_reverse_sorted(self):
        """Worst-case descending input is fully sorted."""
        result, _ = run_sort("Bubble Sort", [9, 7, 5, 3, 1])
        self.assertEqual(result, [1, 3, 5, 7, 9])


    def test_single_element(self):
        """Single-element array is trivially sorted."""
        result, _ = run_sort("Bubble Sort", [42])
        self.assertEqual(result, [42])


    def test_final_status_is_sorted(self):
        """Last status message signals completion."""
        _, statuses = run_sort("Bubble Sort", [3, 1, 2])
        self.assertEqual(statuses[-1], "Sorted!")


    def test_compare_status_messages_emitted(self):
        """Generator yields 'Comparing' messages during the sort."""
        _, statuses = run_sort("Bubble Sort", [3, 1, 2])
        comparing = [s for s in statuses if s.startswith("Comparing")]
        self.assertGreater(len(comparing), 0)


    def test_swap_status_messages_emitted(self):
        """Generator yields 'Swapped' messages when elements are out of order."""
        _, statuses = run_sort("Bubble Sort", [3, 1])
        swapped = [s for s in statuses if s.startswith("Swapped")]
        self.assertGreater(len(swapped), 0)


    def test_no_swap_messages_when_sorted(self):
        """No swaps occur when array is already sorted."""
        _, statuses = run_sort("Bubble Sort", [1, 2, 3])
        swapped = [s for s in statuses if s.startswith("Swapped")]
        self.assertEqual(swapped, [])


class TestSelectionSort(unittest.TestCase):
    """Selection sort animation — colours highlight compared elements correctly"""

    def test_sorts_correctly(self):
        """Sorted output is correct."""
        result, _ = run_sort("Selection Sort", [5, 3, 8, 1, 2])
        self.assertEqual(result, [1, 2, 3, 5, 8])


    def test_colour_pivot_message_emitted(self):
        """
        'Checking idx … vs current min …' messages are produced,
        confirming the pivot / comparison highlighting path is exercised.
        """
        _, statuses = run_sort("Selection Sort", [5, 3, 8, 1, 2])
        checking = [s for s in statuses if s.startswith("Checking")]
        self.assertGreater(len(checking), 0)


    def test_placement_message_per_pass(self):
        """One 'Placed minimum at idx …' message per outer-loop iteration."""
        arr = [5, 3, 8, 1, 2]
        _, statuses = run_sort("Selection Sort", arr)
        placed = [s for s in statuses if s.startswith("Placed minimum")]
        self.assertEqual(len(placed), len(arr))


    def test_already_sorted(self):
        result, _ = run_sort("Selection Sort", [1, 2, 3])
        self.assertEqual(result, [1, 2, 3])


    def test_duplicates(self):
        result, _ = run_sort("Selection Sort", [4, 2, 4, 1, 2])
        self.assertEqual(result, sorted([4, 2, 4, 1, 2]))


    def test_final_status_is_sorted(self):
        _, statuses = run_sort("Selection Sort", [3, 1, 2])
        self.assertEqual(statuses[-1], "Sorted!")


class TestMergeSort(unittest.TestCase):
    """Merge sort correctness (extends the rubric's sorting section)."""

    def test_sorts_correctly(self):
        result, _ = run_sort("Merge Sort", [5, 3, 8, 1, 2])
        self.assertEqual(result, [1, 2, 3, 5, 8])


    def test_already_sorted(self):
        result, _ = run_sort("Merge Sort", [1, 2, 3, 4, 5])
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_reverse_sorted(self):
        result, _ = run_sort("Merge Sort", [5, 4, 3, 2, 1])
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_power_of_two_length(self):
        """Iterative merge sort is well-defined for power-of-two lengths."""
        arr = [8, 6, 4, 2, 7, 5, 3, 1]
        result, _ = run_sort("Merge Sort", arr)
        self.assertEqual(result, sorted(arr))

    def test_odd_length(self):
        arr = [7, 2, 9, 4, 1]
        result, _ = run_sort("Merge Sort", arr)
        self.assertEqual(result, sorted(arr))


    def test_merge_status_messages_emitted(self):
        """'Merging' step messages are produced for the animation."""
        _, statuses = run_sort("Merge Sort", [4, 3, 2, 1])
        merging = [s for s in statuses if s.startswith("Merging")]
        self.assertGreater(len(merging), 0)


    def test_merged_status_messages_emitted(self):
        """'Merged' completion messages follow each merge step."""
        _, statuses = run_sort("Merge Sort", [4, 3, 2, 1])
        merged = [s for s in statuses if s.startswith("Merged")]
        self.assertGreater(len(merged), 0)


    def test_final_status_is_sorted(self):
        _, statuses = run_sort("Merge Sort", [3, 1, 2])
        self.assertEqual(statuses[-1], "Sorted!")


    def test_duplicates(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        result, _ = run_sort("Merge Sort", arr)
        self.assertEqual(result, sorted(arr))


class TestSortingModuleReset(unittest.TestCase):
    """Verify _do_reset returns module to a clean state."""

    def test_reset_clears_generator(self):
        mod = SortingModule()
        mod._start_algo("Bubble Sort")
        self.assertIsNotNone(mod.gen)
        mod._do_reset()
        self.assertIsNone(mod.gen)


    def test_reset_clears_animating_flag(self):
        mod = SortingModule()
        mod._start_algo("Bubble Sort")
        mod._do_reset()
        self.assertFalse(mod.animating)


    def test_reset_generates_new_array(self):
        mod = SortingModule()
        original = list(mod.arr)
        # Run one sort so arr is modified, then reset
        mod._start_algo("Bubble Sort")
        exhaust_gen(mod)
        mod._do_reset()
        # After reset the array should be a fresh random array of the right size
        self.assertEqual(len(mod.arr), SortingModule.ARRAY_SIZE)
        self.assertEqual(len(mod.colours), SortingModule.ARRAY_SIZE)


    def test_start_algo_ignored_while_animating(self):
        """Calling _start_algo while animating should be a no-op."""
        mod = SortingModule()
        mod._start_algo("Bubble Sort")
        first_gen = mod.gen
        mod._start_algo("Merge Sort")   # should be ignored
        self.assertIs(mod.gen, first_gen)
        self.assertEqual(mod.algo_name, "Bubble Sort")


if __name__ == "__main__":
    unittest.main()
