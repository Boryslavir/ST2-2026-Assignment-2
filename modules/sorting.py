import pygame
from cores.globals import (
    BAR_COMPARE,
    BAR_DEFAULT,
    BAR_PIVOT,
    BAR_SORTED,
    BG_COLOUR,
    CLOCK,
    DARK,
    FONT_SM,
    FONT_TITLE,
    HEIGHT,
    SCREEN,
    WIDTH,
)
from cores.setup import (
    draw_text,
    draw_toolbar,
    make_button,
    wait_or_skip
)
from typing import (
    Any,
    Generator
)
from random import randint



class SortingModule:
    """
    Interactive sorting visualiser.
    Keyboard: B = Bubble  S = Selection  M = Merge  R = Reset  ESC = back
    Buttons:  same actions + speed - / +
    """

    ARRAY_SIZE: int = 20
    BAR_MARGIN: int = 4
    CHART_LEFT: int = 40
    CHART_TOP:  int = 100
    CHART_W:    int = WIDTH  - 80
    CHART_H:    int = HEIGHT - 200


    def __init__(self) -> None:
        self._reset_array()
        self.algo_name:  str                        = "None"
        self.status_msg: str                        = "Choose an algorithm to start."
        self.delay:      float                      = 0.08
        self.animating:  bool                       = False
        self.gen:        Generator[Any, Any, Any] | None = None

        btn_h = 36
        self.btn_bubble = pygame.Rect( 40, 50, 110, btn_h)
        self.btn_select = pygame.Rect(165, 50, 120, btn_h)
        self.btn_merge  = pygame.Rect(300, 50, 110, btn_h)
        self.btn_reset  = pygame.Rect(425, 50, 100, btn_h)
        self.btn_slower = pygame.Rect(560, 50,  36, btn_h)
        self.btn_faster = pygame.Rect(604, 50,  36, btn_h)


    # ── Private helpers ────────────────────────────────────────────────────
    def _reset_array(self) -> None:
        self.arr:     list[int]                 = [randint(20, 100) for _ in range(self.ARRAY_SIZE)]
        self.colours: list[tuple[int, int, int]] = [BAR_DEFAULT] * self.ARRAY_SIZE


    def _draw_bars(self) -> None:
        bar_w: int = self.CHART_W // len(self.arr)
        max_v: int = max(self.arr) if self.arr else 1
        for i, (v, colour) in enumerate(zip(self.arr, self.colours)):
            bh   = int((v / max_v) * self.CHART_H)
            rect = pygame.Rect(
                self.CHART_LEFT + i * bar_w + self.BAR_MARGIN,
                self.CHART_TOP  + self.CHART_H - bh,
                bar_w - self.BAR_MARGIN * 2,
                bh,
            )
            pygame.draw.rect(surface=SCREEN, color=colour, rect=rect, border_radius=3)
            pygame.draw.rect(surface=SCREEN, color=DARK,   rect=rect, width=1, border_radius=3)


    def _redraw(self) -> None:
        SCREEN.fill(BG_COLOUR)
        draw_text("Sorting Visualiser", (self.CHART_LEFT, 10), font=FONT_TITLE)
        make_button("Bubble [B]",    self.btn_bubble)
        make_button("Selection [S]", self.btn_select)
        make_button("Merge [M]",     self.btn_merge)
        make_button("Reset [R]",     self.btn_reset)
        make_button("-",             self.btn_slower)
        make_button("+",             self.btn_faster)
        draw_text(f"Speed: {self.delay:.2f}s", (646, 58), font=FONT_SM)
        self._draw_bars()
        draw_toolbar(
            instructions="Algorithm [B/S/M] || Reset [R] || Speed [-/+] || Menu [ESC]",
            status=f"Algorithm: {self.algo_name} | {self.status_msg}",
        )
        pygame.display.flip()


    # ── Sort generators ────────────────────────────────────────────────────
    def _bubble_sort_gen(self) -> Generator[str, Any, None]:
        arr, colours = self.arr, self.colours
        n = len(arr)
        colours[:] = [BAR_DEFAULT] * n
        for i in range(n):
            for j in range(n - i - 1):
                colours[j] = colours[j + 1] = BAR_COMPARE
                yield f"Comparing idx {j} & {j + 1}"
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    yield f"Swapped idx {j} & {j + 1}"
                colours[j] = colours[j + 1] = BAR_DEFAULT
            colours[n - i - 1] = BAR_SORTED
        colours[:] = [BAR_SORTED] * n
        yield "Sorted!"


    def _selection_sort_gen(self) -> Generator[str, Any, None]:
        arr, colours = self.arr, self.colours
        n = len(arr)
        colours[:] = [BAR_DEFAULT] * n
        for i in range(n):
            min_idx    = i
            colours[i] = BAR_PIVOT
            for j in range(i + 1, n):
                colours[j] = BAR_COMPARE
                yield f"Checking idx {j} vs current min ({arr[min_idx]})"
                if arr[j] < arr[min_idx]:
                    if min_idx != i:
                        colours[min_idx] = BAR_DEFAULT
                    min_idx          = j
                    colours[min_idx] = BAR_PIVOT
                else:
                    colours[j] = BAR_DEFAULT
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            colours[i]           = BAR_SORTED
            colours[min_idx]     = BAR_DEFAULT
            yield f"Placed minimum at idx {i}"
        colours[:] = [BAR_SORTED] * n
        yield "Sorted!"


    def _merge_sort_gen(self) -> Generator[str, Any, None]:
        """Iterative bottom-up merge sort; yields a status string each step."""
        arr, colours = self.arr, self.colours
        n = len(arr)
        colours[:] = [BAR_DEFAULT] * n
        width = 1
        while width < n:
            for i in range(0, n, width * 2):
                left  = i
                mid   = min(i + width,       n)
                right = min(i + width * 2,   n)
                for k in range(left, right):
                    colours[k] = BAR_COMPARE
                yield f"Merging [{left}:{mid}] & [{mid}:{right}]"
                merged, l, r = [], left, mid
                while l < mid and r < right:
                    if arr[l] <= arr[r]:
                        merged.append(arr[l]); l += 1
                    else:
                        merged.append(arr[r]); r += 1
                merged += arr[l:mid] + arr[r:right]
                arr[left:right] = merged
                for k in range(left, right):
                    colours[k] = BAR_SORTED
                yield f"Merged [{left}:{right}]"
                for k in range(left, right):
                    colours[k] = BAR_DEFAULT
            width *= 2
        colours[:] = [BAR_SORTED] * n
        yield "Sorted!"


    # ── Dispatch ───────────────────────────────────────────────────────────
    def _start_algo(self, name: str) -> None:
        if self.animating:
            return
        self.algo_name = name
        self.animating = True
        match name:
            case "Bubble Sort":    self.gen = self._bubble_sort_gen()
            case "Selection Sort": self.gen = self._selection_sort_gen()
            case "Merge Sort":     self.gen = self._merge_sort_gen()


    def _do_reset(self) -> None:
        self._reset_array()
        self.algo_name  = "None"
        self.status_msg = "Array reset. Choose an algorithm."
        self.animating  = False
        self.gen        = None


    # ── Public run loop ────────────────────────────────────────────────────
    def run(self) -> None:
        """Block until the user presses ESC, then return to the caller."""
        while True:
            self._redraw()

            if self.animating and self.gen is not None:
                try:
                    self.status_msg = next(self.gen)
                    if wait_or_skip(self.delay):
                        self.animating  = False
                        self.gen        = None
                        self.status_msg = "Stopped. Press R to reset."
                    continue
                except StopIteration:
                    self.animating = False
                    self.gen       = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()

                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE: return
                        case pygame.K_r:      self._do_reset()
                        case pygame.K_b:      self._start_algo("Bubble Sort")
                        case pygame.K_s:      self._start_algo("Selection Sort")
                        case pygame.K_m:      self._start_algo("Merge Sort")

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if   self.btn_bubble.collidepoint(pos): self._start_algo("Bubble Sort")
                    elif self.btn_select.collidepoint(pos): self._start_algo("Selection Sort")
                    elif self.btn_merge .collidepoint(pos): self._start_algo("Merge Sort")
                    elif self.btn_reset .collidepoint(pos): self._do_reset()
                    elif self.btn_slower.collidepoint(pos): self.delay = min(self.delay + 0.02, 0.5)
                    elif self.btn_faster.collidepoint(pos): self.delay = max(self.delay - 0.02, 0.01)

            CLOCK.tick(60)
