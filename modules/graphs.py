import pygame
import math
from collections import deque
from cores.globals import (
    BG_COLOUR,
    CLOCK,
    DARK,
    EDGE_COLOUR,
    FONT,
    FONT_SM,
    FONT_TITLE,
    NODE_CURRENT,
    NODE_DEFAULT,
    NODE_QUEUED,
    NODE_VISITED,
    SCREEN,
)
from cores.setup import (
    draw_text,
    draw_toolbar,
    make_button,
    wait_or_skip
)



class GraphModule:
    """
    BFS and DFS traversal visualiser on a fixed undirected graph.
    Click any node to set it as the start node.
    Keyboard: B = BFS  D = DFS  R = Reset  ESC = back
    """

    NODES: dict[str, tuple[int, int]] = {
        'A': (200, 150),
        'B': (370, 100),
        'C': (540, 150),
        'D': (150, 300),
        'E': (340, 280),
        'F': (550, 300),
        'G': (240, 450),
        'H': (470, 450),
    }
    EDGES: list[tuple[str, str]] = [
        ('A', 'B'), ('A', 'D'),
        ('B', 'C'), ('B', 'E'),
        ('C', 'F'),
        ('D', 'G'), ('D', 'E'),
        ('E', 'F'), ('E', 'H'),
        ('F', 'H'),
        ('G', 'H'),
    ]
    NODE_R: int   = 24
    DELAY:  float = 0.5

    LEGEND: list[tuple[tuple[int, int, int], str]] = [
        (NODE_CURRENT, "Start / Current"),
        (NODE_QUEUED,  "Queued / Frontier"),
        (NODE_VISITED, "Visited"),
        (NODE_DEFAULT, "Unvisited"),
    ]


    def __init__(self) -> None:
        self.adj        = self._build_adj()
        self.start_node = 'A'
        self.algo_name  = "None"
        self.status_msg = "Click a node to set start. B = BFS, D = DFS."
        self.animating  = False
        self.gen        = None
        self._reset_colours()

        btn_h = 36
        self.btn_bfs   = pygame.Rect( 40, 520, 110, btn_h)
        self.btn_dfs   = pygame.Rect(165, 520, 110, btn_h)
        self.btn_reset = pygame.Rect(290, 520, 110, btn_h)


    # ── Private helpers ────────────────────────────────────────────────────
    def _build_adj(self) -> dict[str, list[str]]:
        adj: dict[str, list[str]] = {n: [] for n in self.NODES}
        for u, v in self.EDGES:
            adj[u].append(v)
            adj[v].append(u)
        return adj


    def _reset_colours(self) -> None:
        self.node_colours: dict[str, tuple[int, int, int]] = {
            n: NODE_DEFAULT for n in self.NODES
        }


    def _node_at(self, pos: tuple[int, int]) -> str | None:
        """Return the name of the node under pixel `pos`, or None."""
        for name, npos in self.NODES.items():
            if math.hypot(pos[0] - npos[0], pos[1] - npos[1]) <= self.NODE_R:
                return name
        return None


    def _draw(self) -> None:
        SCREEN.fill(BG_COLOUR)
        draw_text("Graph Traversal", (20, 10), font=FONT_TITLE)

        # Edges
        for u, v in self.EDGES:
            pygame.draw.line(SCREEN, EDGE_COLOUR, self.NODES[u], self.NODES[v], 2)

        # Nodes
        for name, pos in self.NODES.items():
            c = NODE_CURRENT \
                if (name == self.start_node and not self.animating) \
                else self.node_colours[name]
            pygame.draw.circle(SCREEN, c,    pos, self.NODE_R)
            pygame.draw.circle(SCREEN, DARK, pos, self.NODE_R, 2)
            tw = FONT.size(name)[0]
            draw_text(name, (pos[0] - tw // 2, pos[1] - 10))

        # Buttons
        make_button("BFS [B]",   self.btn_bfs)
        make_button("DFS [D]",   self.btn_dfs)
        make_button("Reset [R]", self.btn_reset)

        # Legend (top-right corner)
        lx, ly = 620, 100
        for colour, label in self.LEGEND:
            pygame.draw.circle(SCREEN, colour, (lx, ly), 10)
            draw_text(label, (lx + 16, ly - 10), font=FONT_SM)
            ly += 28

        draw_toolbar(
            instructions="Click node = set start || BFS [B] || DFS [D] || Reset [R] || Menu [ESC]",
            status=f"Algorithm: {self.algo_name} | {self.status_msg}",
        )
        pygame.display.flip()


    # ── Traversal generators ───────────────────────────────────────────────
    def _bfs_gen(self):
        visited: set[str] = set()
        queue = deque([self.start_node])
        self.node_colours[self.start_node] = NODE_QUEUED
        yield f"BFS from {self.start_node}: start enqueued"
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            self.node_colours[node] = NODE_CURRENT
            yield f"Visiting {node}"
            for nb in sorted(self.adj[node]):
                if nb not in visited:
                    self.node_colours[nb] = NODE_QUEUED
                    queue.append(nb)
                    yield f"Queued neighbour {nb}"
            self.node_colours[node] = NODE_VISITED
            yield f"Finished {node}"
        yield "BFS complete!"


    def _dfs_gen(self):
        visited: set[str] = set()
        stack = [self.start_node]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            self.node_colours[node] = NODE_CURRENT
            yield f"Visiting {node}"
            for nb in sorted(self.adj[node], reverse=True):
                if nb not in visited:
                    self.node_colours[nb] = NODE_QUEUED
                    stack.append(nb)
            self.node_colours[node] = NODE_VISITED
            yield f"Explored {node}"
        yield "DFS complete!"


    # ── Dispatch ───────────────────────────────────────────────────────────
    def _start_algo(self, name: str) -> None:
        if self.animating:
            return
        self.algo_name = name
        self._reset_colours()
        self.animating = True
        self.gen = self._bfs_gen() if name == "BFS" else self._dfs_gen()


    def _do_reset(self) -> None:
        self._reset_colours()
        self.algo_name  = "None"
        self.animating  = False
        self.gen        = None
        self.status_msg = f"Reset. Start node: {self.start_node}"


    # ── Public run loop ────────────────────────────────────────────────────
    def run(self) -> None:
        while True:
            self._draw()

            if self.animating and self.gen is not None:
                try:
                    self.status_msg = next(self.gen)
                    if wait_or_skip(self.DELAY):
                        self.animating  = False
                        self.gen        = None
                        self.status_msg = "Stopped."
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
                        case pygame.K_b:      self._start_algo("BFS")
                        case pygame.K_d:      self._start_algo("DFS")
                        case pygame.K_r:      self._do_reset()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos     = event.pos
                    clicked = self._node_at(pos)
                    if clicked and not self.animating:
                        self.start_node = clicked
                        self._reset_colours()
                        self.status_msg = f"Start node set to {clicked}"
                    elif self.btn_bfs  .collidepoint(pos): self._start_algo("BFS")
                    elif self.btn_dfs  .collidepoint(pos): self._start_algo("DFS")
                    elif self.btn_reset.collidepoint(pos): self._do_reset()

            CLOCK.tick(60)
