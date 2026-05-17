
import os
import sys
import unittest
from unittest.mock import MagicMock


# Prevent Pygame / SDL from trying to open a display in a headless environment
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


# Make sure the project root is on the path when running from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import pygame
pygame.init()


from modules.puzzles import (
    lerp,
    pf_neighbors,
    pf_heuristic,
    _dp_compute,
    _dp_sample_path,
    _dp_format,
    _eq_heap_pos,
    _eq_lerp_xy,
    EQEvent,
    Button,
    build_fonts,
)
from cores.globals import PF_ROWS, PF_COLS, DP_ROWS, DP_COLS, EQ_TOP_MARGIN


class TestLerp(unittest.TestCase):
    """Colour interpolation — lerp produces correct blended RGB tuples"""

    def test_lerp_at_zero_returns_first_colour(self):
        """t=0 returns the first colour exactly."""
        self.assertEqual(lerp((0, 0, 0), (255, 255, 255), 0.0), (0, 0, 0))


    def test_lerp_at_one_returns_second_colour(self):
        """t=1 returns the second colour exactly."""
        self.assertEqual(lerp((0, 0, 0), (255, 255, 255), 1.0), (255, 255, 255))


    def test_lerp_at_half_returns_midpoint(self):
        """t=0.5 returns the component-wise midpoint of the two colours."""
        self.assertEqual(lerp((0, 0, 0), (200, 100, 50), 0.5), (100, 50, 25))


    def test_lerp_returns_integer_components(self):
        """All returned RGB components must be integers, never floats."""
        for component in lerp((0, 0, 0), (100, 100, 100), 0.33):
            self.assertIsInstance(component, int)


class TestPathfindingHeuristic(unittest.TestCase):
    """A* heuristic — Manhattan distance computed correctly"""

    def test_distance_to_self_is_zero(self):
        """Distance from a point to itself is 0."""
        self.assertEqual(pf_heuristic((3, 4), (3, 4)), 0)


    def test_pure_horizontal_distance(self):
        """Horizontal distance equals column difference."""
        self.assertEqual(pf_heuristic((0, 0), (0, 5)), 5)


    def test_pure_vertical_distance(self):
        """Vertical distance equals row difference."""
        self.assertEqual(pf_heuristic((0, 0), (5, 0)), 5)


    def test_diagonal_sums_components(self):
        """Diagonal distance equals |dr| + |dc| (Manhattan)."""
        self.assertEqual(pf_heuristic((0, 0), (3, 4)), 7)


class TestPathfindingNeighbors(unittest.TestCase):
    """Pathfinding neighbours — walls and boundaries excluded correctly"""

    def setUp(self):
        self.grid = [[0] * PF_COLS for _ in range(PF_ROWS)]


    def test_interior_cell_has_four_neighbours(self):
        """An open interior cell yields all four orthogonal neighbours."""
        result = list(pf_neighbors((5, 5), self.grid))
        self.assertEqual(len(result), 4)
        self.assertIn((4, 5), result)
        self.assertIn((6, 5), result)
        self.assertIn((5, 4), result)
        self.assertIn((5, 6), result)


    def test_top_left_corner_has_two_neighbours(self):
        """A corner cell yields only two neighbours (boundary clipping)."""
        result = list(pf_neighbors((0, 0), self.grid))
        self.assertEqual(len(result), 2)
        self.assertIn((0, 1), result)
        self.assertIn((1, 0), result)


    def test_bottom_right_corner_has_two_neighbours(self):
        """The opposite corner also yields exactly two neighbours."""
        result = list(pf_neighbors((PF_ROWS - 1, PF_COLS - 1), self.grid))
        self.assertEqual(len(result), 2)


    def test_walls_excluded_from_neighbours(self):
        """A wall (value 1) is never returned as a neighbour."""
        self.grid[5][6] = 1
        result = list(pf_neighbors((5, 5), self.grid))
        self.assertNotIn((5, 6), result)
        self.assertEqual(len(result), 3)


    def test_fully_walled_cell_has_no_neighbours(self):
        """A cell with walls on all four sides yields zero neighbours."""
        self.grid[4][5] = 1
        self.grid[6][5] = 1
        self.grid[5][4] = 1
        self.grid[5][6] = 1
        self.assertEqual(list(pf_neighbors((5, 5), self.grid)), [])


class TestDPCompute(unittest.TestCase):
    """DP grid path count — table values match expected counts"""

    def setUp(self):
        self.wall = [[False] * DP_COLS for _ in range(DP_ROWS)]


    def test_origin_cell_always_has_one_path(self):
        """dp[0][0] equals 1 (the empty path to the start)."""
        dp, _, _ = _dp_compute(self.wall)
        self.assertEqual(dp[0][0], 1)


    def test_empty_grid_has_positive_path_count(self):
        """An unblocked grid has at least one route to the goal."""
        _, _, total = _dp_compute(self.wall)
        self.assertGreater(total, 0)


    def test_fill_order_visits_every_cell_once(self):
        """The DP fill order must visit every cell exactly once."""
        _, order, _ = _dp_compute(self.wall)
        self.assertEqual(len(order), DP_ROWS * DP_COLS)
        self.assertEqual(len(set(order)), DP_ROWS * DP_COLS)


    def test_walling_off_goal_gives_zero_paths(self):
        """Blocking both neighbours of the goal eliminates all paths."""
        self.wall[DP_ROWS - 2][DP_COLS - 1] = True
        self.wall[DP_ROWS - 1][DP_COLS - 2] = True
        _, _, total = _dp_compute(self.wall)
        self.assertEqual(total, 0)


    def test_first_column_only_one_way_down(self):
        """With the first row blocked, every first-column cell has exactly 1 path."""
        for c in range(1, DP_COLS):
            self.wall[0][c] = True
        dp, _, _ = _dp_compute(self.wall)
        for r in range(DP_ROWS):
            self.assertEqual(dp[r][0], 1)


class TestDPSamplePath(unittest.TestCase):
    """DP grid sampled path — random path is valid (start→goal, only right/down)"""

    def setUp(self):
        self.wall = [[False] * DP_COLS for _ in range(DP_ROWS)]
        self.dp, _, _ = _dp_compute(self.wall)


    def test_path_starts_at_origin(self):
        """Every sampled path begins at (0, 0)."""
        path = _dp_sample_path(self.dp, self.wall)
        self.assertEqual(path[0], (0, 0))


    def test_path_ends_at_goal(self):
        """Every sampled path ends at the bottom-right cell."""
        path = _dp_sample_path(self.dp, self.wall)
        self.assertEqual(path[-1], (DP_ROWS - 1, DP_COLS - 1))


    def test_path_length_is_taxicab_plus_one(self):
        """A monotonic path on an R×C grid has exactly R + C - 1 cells."""
        path = _dp_sample_path(self.dp, self.wall)
        self.assertEqual(len(path), DP_ROWS + DP_COLS - 1)


    def test_path_only_moves_right_or_down(self):
        """Each step in the path is exactly one right or one down move."""
        path = _dp_sample_path(self.dp, self.wall)
        for prev, curr in zip(path, path[1:]):
            dr = curr[0] - prev[0]
            dc = curr[1] - prev[1]
            self.assertIn((dr, dc), [(0, 1), (1, 0)])


    def test_unreachable_goal_returns_empty(self):
        """When no path exists, the sampler returns an empty list."""
        wall = [[False] * DP_COLS for _ in range(DP_ROWS)]
        wall[DP_ROWS - 2][DP_COLS - 1] = True
        wall[DP_ROWS - 1][DP_COLS - 2] = True
        dp, _, _ = _dp_compute(wall)
        self.assertEqual(_dp_sample_path(dp, wall), [])


class TestDPFormat(unittest.TestCase):
    """Number formatter — large integers formatted with k / M / scientific notation"""

    def test_below_thousand_returns_plain_int_string(self):
        """Values under 1000 are shown as plain integers."""
        self.assertEqual(_dp_format(0), "0")
        self.assertEqual(_dp_format(42), "42")
        self.assertEqual(_dp_format(999), "999")


    def test_thousands_use_k_suffix(self):
        """Values between 1k and 1M use the 'k' suffix."""
        self.assertEqual(_dp_format(1_000), "1.0k")
        self.assertEqual(_dp_format(12_500), "12.5k")


    def test_millions_use_m_suffix(self):
        """Values between 1M and 1B use the 'M' suffix."""
        self.assertEqual(_dp_format(1_000_000), "1.0M")
        self.assertEqual(_dp_format(2_500_000), "2.5M")


    def test_billions_use_scientific_notation(self):
        """Values >= 1B fall back to scientific notation (contains 'e')."""
        result = _dp_format(1_000_000_000)
        self.assertIn("e", result)


class TestEQHeapPos(unittest.TestCase):
    """Heap node positioning — geometric layout properties are correct"""

    def test_root_y_equals_top_margin(self):
        """The root node (index 0) sits exactly at the top margin."""
        _, y = _eq_heap_pos(0, 1)
        self.assertEqual(y, EQ_TOP_MARGIN)


    def test_children_are_below_parent(self):
        """A child node has a greater y coordinate than its parent."""
        _, y_parent = _eq_heap_pos(0, 3)
        _, y_child  = _eq_heap_pos(1, 3)
        self.assertGreater(y_child, y_parent)


    def test_siblings_share_y_coordinate(self):
        """Sibling nodes (e.g. indices 1 and 2) share a y coordinate."""
        _, y_left  = _eq_heap_pos(1, 3)
        _, y_right = _eq_heap_pos(2, 3)
        self.assertEqual(y_left, y_right)


    def test_left_sibling_is_left_of_right_sibling(self):
        """The left child has a smaller x coordinate than the right child."""
        x_left,  _ = _eq_heap_pos(1, 3)
        x_right, _ = _eq_heap_pos(2, 3)
        self.assertLess(x_left, x_right)


class TestEQLerpXY(unittest.TestCase):
    """2D point interpolation — animation positions interpolated correctly"""

    def test_t_zero_returns_start_point(self):
        """t=0 returns the start point exactly."""
        self.assertEqual(_eq_lerp_xy((0, 0), (10, 20), 0.0), (0, 0))


    def test_t_one_returns_end_point(self):
        """t=1 returns the end point exactly."""
        self.assertEqual(_eq_lerp_xy((0, 0), (10, 20), 1.0), (10, 20))


    def test_t_half_returns_midpoint(self):
        """t=0.5 returns the midpoint of the two points."""
        self.assertEqual(_eq_lerp_xy((0, 0), (10, 20), 0.5), (5, 10))


class TestEQEvent(unittest.TestCase):
    """Event-queue priority — min-heap ordering on (priority, seq) is correct"""

    def test_lower_priority_value_orders_first(self):
        """An event with priority 1 orders before one with priority 2."""
        high = EQEvent(priority=1, seq=1, label="A")
        low  = EQEvent(priority=2, seq=2, label="B")
        self.assertLess(high, low)


    def test_equal_priority_broken_by_sequence(self):
        """When priorities tie, the lower seq number orders first."""
        first  = EQEvent(priority=1, seq=1, label="A")
        second = EQEvent(priority=1, seq=2, label="B")
        self.assertLess(first, second)


    def test_label_is_not_part_of_ordering(self):
        """The label field is compare=False and must not affect ordering."""
        a = EQEvent(priority=1, seq=1, label="ZZZ")
        b = EQEvent(priority=1, seq=2, label="AAA")
        self.assertLess(a, b)


class TestButton(unittest.TestCase):
    """Button widget — click and hover events handled correctly"""

    def test_button_stores_rect_dimensions(self):
        """Button initialises a pygame.Rect with the correct dimensions."""
        b = Button((10, 20, 100, 40), "OK", lambda: None)
        self.assertEqual((b.rect.x, b.rect.y), (10, 20))
        self.assertEqual((b.rect.width, b.rect.height), (100, 40))


    def test_left_click_inside_fires_callback(self):
        """A left-click inside the button rect triggers the callback exactly once."""
        called = []
        b = Button((0, 0, 100, 100), "OK", lambda: called.append(True))
        event = MagicMock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 50))
        b.handle(event)
        self.assertEqual(called, [True])


    def test_left_click_outside_does_not_fire_callback(self):
        """A left-click outside the button rect does not fire the callback."""
        called = []
        b = Button((0, 0, 100, 100), "OK", lambda: called.append(True))
        event = MagicMock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 200))
        b.handle(event)
        self.assertEqual(called, [])


    def test_right_click_does_not_fire_callback(self):
        """Only left-clicks (button 1) trigger the callback; right-clicks are ignored."""
        called = []
        b = Button((0, 0, 100, 100), "OK", lambda: called.append(True))
        event = MagicMock(type=pygame.MOUSEBUTTONDOWN, button=3, pos=(50, 50))
        b.handle(event)
        self.assertEqual(called, [])


    def test_hover_becomes_true_inside_rect(self):
        """Mouse motion inside the rect sets the hover flag to True."""
        b = Button((0, 0, 100, 100), "OK", lambda: None)
        event = MagicMock(type=pygame.MOUSEMOTION, pos=(50, 50))
        b.handle(event)
        self.assertTrue(b._hover)


    def test_hover_becomes_false_outside_rect(self):
        """Mouse motion outside the rect clears the hover flag."""
        b = Button((0, 0, 100, 100), "OK", lambda: None)
        b._hover = True
        event = MagicMock(type=pygame.MOUSEMOTION, pos=(200, 200))
        b.handle(event)
        self.assertFalse(b._hover)


class TestBuildFonts(unittest.TestCase):
    """Font builder — all expected fonts are constructed and usable"""

    def test_build_fonts_returns_all_expected_keys(self):
        """The font dict contains 'title', 'body', and 'small' keys."""
        fonts = build_fonts()
        self.assertIn("title", fonts)
        self.assertIn("body",  fonts)
        self.assertIn("small", fonts)


    def test_fonts_can_render_text(self):
        """Each font can render a non-empty pygame Surface."""
        fonts = build_fonts()
        for name, font in fonts.items():
            surface = font.render("test", True, (0, 0, 0))
            self.assertGreater(surface.get_width(), 0, f"font '{name}' failed")


if __name__ == "__main__":
    unittest.main()