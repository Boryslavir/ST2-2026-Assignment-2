import pygame
import math
from cores.globals import (
    BG_COLOUR,
    CLOCK,
    DARK,
    EDGE_COLOUR,
    FONT_SM,
    FONT_TITLE,
    HEAP_HIGHLIGHT,
    HEAP_NODE,
    SCREEN,
    WHITE,
    WIDTH,
)
from cores.setup import (
    draw_text,
    draw_toolbar,
    make_button,
    wait_or_skip
)


class HeapModule:
    """
    Min-heap visualiser with step-by-step sift animations.
    Type an integer + ENTER to insert.
    Keyboard: E = extract-min  R = reset  ESC = back
    """

    NODE_R:     int   = 22
    SIFT_DELAY: float = 0.5
    PRELOAD:    list[int] = [40, 70, 30, 90, 50, 20, 60]


    def __init__(self) -> None:
        self.data:       list[int]  = []
        self.highlight:  set[int]   = set()
        self.input_buf:  str        = ""
        self.status_msg: str        = "Type a number + ENTER to insert.  E = extract min."

        for v in self.PRELOAD:
            self._heap_insert(v)   # silent insert (no animation) for preload

        btn_h = 36
        self.btn_extract = pygame.Rect( 40, 520, 140, btn_h)
        self.btn_reset   = pygame.Rect(195, 520, 110, btn_h)


    # ── Pure heap logic (no animation) ────────────────────────────────────
    def _heap_insert(self, val: int) -> None:
        self.data.append(val)
        self._sift_up_silent(len(self.data) - 1)


    def _sift_up_silent(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self.data[i] < self.data[parent]:
                self.data[i], self.data[parent] = self.data[parent], self.data[i]
                i = parent
            else:
                break


    def _sift_down_silent(self, i: int) -> None:
        n = len(self.data)
        while True:
            smallest = i
            l, r     = 2 * i + 1, 2 * i + 2
            if l < n and self.data[l] < self.data[smallest]: smallest = l
            if r < n and self.data[r] < self.data[smallest]: smallest = r
            if smallest == i:
                break
            self.data[i], self.data[smallest] = self.data[smallest], self.data[i]
            i = smallest


    # ── Node position ──────────────────────────────────────────────────────
    def _node_pos(self, index: int) -> tuple[int, int]:
        """Map heap array index to (x, y) pixel position in the tree display."""
        if index == 0:
            return (WIDTH // 2, 110)
        level        = int(math.log2(index + 1))
        pos_in_level = index - (2 ** level - 1)
        nodes_in_lvl = 2 ** level
        spacing_x    = min(WIDTH - 100, 600) / nodes_in_lvl
        x = 50 + spacing_x * pos_in_level + spacing_x / 2
        y = 110 + level * 80
        return (int(x), int(y))


    # ── Drawing ────────────────────────────────────────────────────────────
    def _draw(self) -> None:
        SCREEN.fill(BG_COLOUR)
        draw_text("Heap Visualiser (Min-Heap)", (20, 10), font=FONT_TITLE)

        n = len(self.data)

        # Edges first so nodes render on top
        for i in range(1, n):
            parent = (i - 1) // 2
            pygame.draw.line(SCREEN, EDGE_COLOUR, self._node_pos(parent), self._node_pos(i), 2)

        # Nodes
        for i, val in enumerate(self.data):
            pos = self._node_pos(i)
            c   = HEAP_HIGHLIGHT if i in self.highlight else HEAP_NODE
            pygame.draw.circle(SCREEN, c,    pos, self.NODE_R)
            pygame.draw.circle(SCREEN, DARK, pos, self.NODE_R, 2)
            label = str(val)
            tw    = FONT_SM.size(label)[0]
            draw_text(label, (pos[0] - tw // 2, pos[1] - 10), font=FONT_SM)

        # Input box
        draw_text("Insert value:", (40, 472), font=FONT_SM)
        input_rect = pygame.Rect(160, 468, 120, 36)
        pygame.draw.rect(SCREEN, WHITE, input_rect, border_radius=4)
        pygame.draw.rect(SCREEN, DARK,  input_rect, 2, border_radius=4)
        draw_text(self.input_buf + "|", (input_rect.x + 6, input_rect.y + 8), font=FONT_SM)

        make_button("Extract Min [E]", self.btn_extract)
        make_button("Reset [R]",       self.btn_reset)

        draw_toolbar(
            instructions="Number + ENTER = insert || Extract Min [E] || Reset [R] || Menu [ESC]",
            status=self.status_msg,
        )
        pygame.display.flip()


    # ── Animated sift operations ───────────────────────────────────────────
    def _animate_insert(self, val: int) -> None:
        """Append `val` then sift-up with per-swap highlighting."""
        self.data.append(val)
        i = len(self.data) - 1
        while i > 0:
            parent = (i - 1) // 2
            if self.data[i] < self.data[parent]:
                self.highlight  = {i, parent}
                self.status_msg = f"Sift-up: swapping idx {i} and {parent}"
                self._draw()
                if wait_or_skip(self.SIFT_DELAY):
                    break
                self.data[i], self.data[parent] = self.data[parent], self.data[i]
                i = parent
            else:
                break
        self.highlight  = set()
        self.status_msg = f"Inserted {val}. Heap size = {len(self.data)}"


    def _animate_extract(self) -> None:
        """Remove the minimum and sift-down with per-swap highlighting."""
        if not self.data:
            self.status_msg = "Heap is empty!"
            return
        extracted = self.data[0]
        if len(self.data) == 1:
            self.data.pop()
            self.status_msg = f"Extracted min = {extracted}. Heap is now empty."
            return
        self.data[0] = self.data.pop()
        i, n = 0, len(self.data)
        while True:
            smallest = i
            l, r     = 2 * i + 1, 2 * i + 2
            if l < n and self.data[l] < self.data[smallest]: smallest = l
            if r < n and self.data[r] < self.data[smallest]: smallest = r
            if smallest == i:
                break
            self.highlight  = {i, smallest}
            self.status_msg = f"Sift-down: swapping idx {i} and {smallest}"
            self._draw()
            if wait_or_skip(self.SIFT_DELAY):
                break
            self.data[i], self.data[smallest] = self.data[smallest], self.data[i]
            i = smallest
        self.highlight  = set()
        self.status_msg = f"Extracted min = {extracted}. Heap size = {len(self.data)}"


    def _do_reset(self) -> None:
        self.data       = []
        self.highlight  = set()
        self.input_buf  = ""
        self.status_msg = "Heap reset."


    # ── Public run loop ────────────────────────────────────────────────────
    def run(self) -> None:
        while True:
            self._draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()

                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            return
                        case pygame.K_e:
                            self._animate_extract()
                        case pygame.K_r:
                            self._do_reset()
                        case pygame.K_RETURN:
                            try:
                                self._animate_insert(int(self.input_buf))
                            except ValueError:
                                self.status_msg = "Please enter a valid integer."
                            finally:
                                self.input_buf = ""
                        case pygame.K_BACKSPACE:
                            self.input_buf = self.input_buf[:-1]
                        case _:
                            if event.unicode.isdigit() or (
                                event.unicode == '-' and not self.input_buf
                            ):
                                self.input_buf += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if   self.btn_extract.collidepoint(pos): self._animate_extract()
                    elif self.btn_reset  .collidepoint(pos): self._do_reset()

            CLOCK.tick(60)
