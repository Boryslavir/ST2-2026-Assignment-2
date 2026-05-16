def puzzles_module():
   """
Puzzles module — three interactive visualisers:

  1. Pathfinding   — A* on a clickable grid
  2. Event Queue   — priority-heap discrete-event simulator
  3. DP Grid       — dynamic-programming path counter

Adapted from three reference files that originally depended on a separate
`ui.theme` module. That dependency has been replaced with a local `_theme`
namespace and `_Button` helper defined inside this file, so no external
`ui/` package is needed.

Controls
    - Main picker:    click a card to enter, ESC to leave puzzles
    - Inside any puzzle: ESC returns to the picker
"""
import pygame
import heapq
import math
import random
from dataclasses import dataclass, field
from sys import exit
from types import SimpleNamespace

from cores.globals import (
    CLOCK,
    HEIGHT,
    WIDTH,
)


# =============================================================================
#                LOCAL THEME (replaces `from ui import theme`)
# =============================================================================

# Layout
_HEADER_H = 60

# Palette
_TEXT          = ( 35,  35,  50)
_DIM           = (110, 110, 130)
_EMPTY_COL     = (235, 235, 248)
_WALL_COL      = ( 60,  60,  80)
_START_COL     = ( 80, 200, 120)
_START_GLOW    = (180, 250, 200)
_END_COL       = (240,  80,  80)
_END_GLOW      = (255, 180, 180)
_PATH_COL      = (240, 200,  50)
_PATH_GLOW     = (255, 245, 200)
_FRONTIER_COL  = (250, 220, 100)
_VISITED_COL   = (140, 200, 240)
_EDGE_COL      = (160, 160, 180)
_PANEL_BG      = (220, 220, 240)
_PANEL_LINE    = (150, 150, 180)
_SUCCESS       = ( 90, 200, 130)
_DANGER        = (230, 100, 100)
_WARNING       = (240, 200,  80)

# Priority colours: index 1=Critical .. 5=Trivial
_PRIO_COL = [
    (  0,   0,   0),    # 0 unused
    (230,  80,  80),
    (240, 150,  80),
    (240, 220, 100),
    (100, 200, 150),
    (120, 170, 220),
]


def _lerp(a, b, t):
    """Linear-interpolate two RGB tuples by t in [0, 1]."""
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def _make_background():
    """Vertical gradient backdrop, computed once and reused per frame."""
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = _lerp((248, 248, 255), (215, 220, 245), t)
        pygame.draw.line(surf, c, (0, y), (WIDTH, y))
    return surf


def _screen():
    """Lazily fetch the active pygame display surface."""
    return pygame.display.get_surface()


def _draw_header(title: str, subtitle: str, fonts) -> None:
    pygame.draw.rect(_screen(), _PANEL_BG, (0, 0, WIDTH, _HEADER_H))
    pygame.draw.line(_screen(), _PANEL_LINE, (0, _HEADER_H), (WIDTH, _HEADER_H), 2)
    _screen().blit(fonts['title'].render(title, True, _TEXT),  (20, 8))
    _screen().blit(fonts['small'].render(subtitle, True, _DIM), (20, 38))


class _Button:
    """Minimal clickable button with label and optional fill colour."""

    def __init__(self, rect, label, callback, color=None):
        self.rect     = pygame.Rect(*rect) if not isinstance(rect, pygame.Rect) else rect
        self.label    = label
        self.callback = callback
        self.color    = color or _PANEL_LINE
        self._hover   = False

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, surface, font):
        fill = _lerp(self.color, (255, 255, 255), 0.25) if self._hover else self.color
        pygame.draw.rect(surface, fill,  self.rect, border_radius=6)
        pygame.draw.rect(surface, _TEXT, self.rect, width=1, border_radius=6)
        text = font.render(self.label, True, _TEXT)
        surface.blit(text, (
            self.rect.centerx - text.get_width()  // 2,
            self.rect.centery - text.get_height() // 2,
        ))


# Theme namespace mirroring the original `ui.theme` API the reference files used.
theme = SimpleNamespace(
    WIDTH        = WIDTH,
    HEIGHT       = HEIGHT,
    HEADER_H     = _HEADER_H,
    TEXT         = _TEXT,
    DIM          = _DIM,
    EMPTY_COL    = _EMPTY_COL,
    WALL_COL     = _WALL_COL,
    START_COL    = _START_COL,
    START_GLOW   = _START_GLOW,
    END_COL      = _END_COL,
    END_GLOW     = _END_GLOW,
    PATH_COL     = _PATH_COL,
    PATH_GLOW    = _PATH_GLOW,
    FRONTIER_COL = _FRONTIER_COL,
    VISITED_COL  = _VISITED_COL,
    EDGE_COL     = _EDGE_COL,
    PANEL_BG     = _PANEL_BG,
    PANEL_LINE   = _PANEL_LINE,
    SUCCESS      = _SUCCESS,
    DANGER       = _DANGER,
    WARNING      = _WARNING,
    PRIO_COL     = _PRIO_COL,
    lerp         = _lerp,
    make_background = _make_background,
    draw_header     = _draw_header,
    Button          = _Button,
)


def _build_fonts():
    """Create the fonts dict that the three sub-puzzles expect."""
    return {
        'title': pygame.font.SysFont(name=None, size=32),
        'body':  pygame.font.SysFont(name=None, size=22),
        'small': pygame.font.SysFont(name=None, size=18),
    }


# =============================================================================
#                       PUZZLE 1 — PATHFINDING (A*)
# =============================================================================

_PF_CELL   = 22
_PF_COLS   = 28
_PF_ROWS   = 17
_PF_GRID_W = _PF_COLS * _PF_CELL
_PF_GRID_H = _PF_ROWS * _PF_CELL
_PF_GRID_X = (WIDTH - _PF_GRID_W) // 2
_PF_GRID_Y = _HEADER_H + 50

_PF_PAD             = 2
_PF_CORNER          = 4
_PF_FADE_MS         = 280
_PF_PATH_REVEAL_MS  = 22
_PF_STEPS_PER_FRAME = 2


def _pf_neighbors(cell, grid):
    r, c = cell
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < _PF_ROWS and 0 <= nc < _PF_COLS and grid[nr][nc] != 1:
            yield (nr, nc)


def _pf_heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _run_pathfinding(fonts):
    screen = _screen()
    grid   = [[0] * _PF_COLS for _ in range(_PF_ROWS)]
    state  = {
        "start": None, "end": None, "mode": "EDIT",
        "visited": {}, "frontier": {}, "path_list": [], "path_index": {},
        "path_reveal_t": 0,
        "open_heap": [], "came_from": {}, "g_score": {}, "counter": 0,
    }
    bg = theme.make_background()

    def init_search():
        s, e = state["start"], state["end"]
        state["open_heap"] = []
        state["came_from"] = {}
        state["g_score"]   = {s: 0}
        state["counter"]   = 0
        heapq.heappush(state["open_heap"], (_pf_heuristic(s, e), 0, s))
        now = pygame.time.get_ticks()
        state["visited"]    = {}
        state["frontier"]   = {s: now}
        state["path_list"]  = []
        state["path_index"] = {}

    def step_search():
        if not state["open_heap"]:
            state["mode"] = "DONE"
            return True
        _, _, current = heapq.heappop(state["open_heap"])
        if current in state["visited"]:
            return False
        if current == state["end"]:
            seq = [current]
            while seq[-1] in state["came_from"]:
                seq.append(state["came_from"][seq[-1]])
            seq.reverse()
            state["path_list"]     = seq
            state["path_index"]    = {c: i for i, c in enumerate(seq)}
            state["path_reveal_t"] = pygame.time.get_ticks()
            state["mode"]          = "DONE"
            return True
        now = pygame.time.get_ticks()
        state["visited"][current] = now
        state["frontier"].pop(current, None)
        for nb in _pf_neighbors(current, grid):
            t = state["g_score"][current] + 1
            if nb not in state["g_score"] or t < state["g_score"][nb]:
                state["came_from"][nb] = current
                state["g_score"][nb]   = t
                state["counter"]      += 1
                heapq.heappush(
                    state["open_heap"],
                    (t + _pf_heuristic(nb, state["end"]), state["counter"], nb),
                )
                if nb not in state["visited"]:
                    state["frontier"][nb] = now
        return False

    def reset_search():
        state["visited"]    = {}
        state["frontier"]   = {}
        state["path_list"]  = []
        state["path_index"] = {}
        state["mode"]       = "EDIT"

    def clear_all():
        for r in range(_PF_ROWS):
            for c in range(_PF_COLS):
                grid[r][c] = 0
        state["start"] = None
        state["end"]   = None
        reset_search()

    def cell_at(pos):
        x, y = pos
        if not (_PF_GRID_X <= x < _PF_GRID_X + _PF_GRID_W and
                _PF_GRID_Y <= y < _PF_GRID_Y + _PF_GRID_H):
            return None
        return ((y - _PF_GRID_Y) // _PF_CELL, (x - _PF_GRID_X) // _PF_CELL)

    def paint(pos, button):
        if state["mode"] != "EDIT":
            return
        rc = cell_at(pos)
        if rc is None:
            return
        r, c = rc
        if button == 1:
            if state["start"] is None:
                state["start"] = (r, c); grid[r][c] = 2
            elif state["end"] is None and (r, c) != state["start"]:
                state["end"]   = (r, c); grid[r][c] = 3
            elif grid[r][c] == 0:
                grid[r][c] = 1
        elif button == 3:
            if (r, c) == state["start"]: state["start"] = None
            if (r, c) == state["end"]:   state["end"]   = None
            grid[r][c] = 0

    def start_run():
        if state["mode"] == "EDIT" and state["start"] and state["end"]:
            init_search()
            state["mode"] = "RUNNING"

    btns = [
        theme.Button((40,  555, 90, 36), "RUN",   start_run,   color=theme.SUCCESS),
        theme.Button((140, 555, 90, 36), "RESET", reset_search),
        theme.Button((240, 555, 90, 36), "CLEAR", clear_all,   color=theme.DANGER),
        theme.Button((WIDTH - 100, 555, 80, 36), "BACK",
                     lambda: state.update(_exit=True)),
    ]

    dragging = False
    drag_btn = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "menu"
                if event.key == pygame.K_SPACE:  start_run()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                paint(event.pos, event.button)
                dragging = True
                drag_btn = event.button
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                paint(event.pos, drag_btn)
            for b in btns:
                b.handle(event)

        if state.get("_exit"):
            return "menu"

        if state["mode"] == "RUNNING":
            for _ in range(_PF_STEPS_PER_FRAME):
                if step_search():
                    break

        now = pygame.time.get_ticks()

        screen.blit(bg, (0, 0))
        theme.draw_header(
            "Pathfinding (A*)",
            "L-click: start, end, walls   R-click: erase   SPACE: run   ESC: back",
            fonts,
        )

        info = fonts['body'].render(
            f"visited {len(state['visited'])}   "
            f"frontier {len(state['frontier'])}   " +
            (f"path length {len(state['path_list']) - 1}"
             if state["path_list"] else
             ("no path" if state["mode"] == "DONE" else "")),
            True, theme.TEXT,
        )
        screen.blit(info, (40, _HEADER_H + 15))

        # Draw cells
        path_index = state["path_index"]
        for r in range(_PF_ROWS):
            for c in range(_PF_COLS):
                rect = pygame.Rect(
                    _PF_GRID_X + c * _PF_CELL + _PF_PAD,
                    _PF_GRID_Y + r * _PF_CELL + _PF_PAD,
                    _PF_CELL - 2 * _PF_PAD,
                    _PF_CELL - 2 * _PF_PAD,
                )
                pos  = (r, c)
                base = grid[r][c]

                color = theme.EMPTY_COL
                if state["path_list"] and pos in path_index:
                    elapsed = now - state["path_reveal_t"]
                    if path_index[pos] * _PF_PATH_REVEAL_MS <= elapsed:
                        pulse = (math.sin(now / 250 + path_index[pos] * 0.3) + 1) * 0.5
                        color = theme.lerp(theme.PATH_COL, theme.PATH_GLOW, pulse * 0.4)
                elif base == 2:
                    pulse = (math.sin(now / 280) + 1) * 0.5
                    color = theme.lerp(theme.START_COL, theme.START_GLOW, pulse * 0.5)
                elif base == 3:
                    pulse = (math.sin(now / 280 + 1.5) + 1) * 0.5
                    color = theme.lerp(theme.END_COL, theme.END_GLOW, pulse * 0.5)
                elif base == 1:
                    color = theme.WALL_COL
                elif pos in state["visited"]:
                    t = min(1.0, (now - state["visited"][pos]) / _PF_FADE_MS)
                    color = theme.lerp(theme.FRONTIER_COL, theme.VISITED_COL, t)
                elif pos in state["frontier"]:
                    t = min(1.0, (now - state["frontier"][pos]) / _PF_FADE_MS)
                    color = theme.lerp(theme.EMPTY_COL, theme.FRONTIER_COL, t)

                pygame.draw.rect(screen, color, rect, border_radius=_PF_CORNER)

        for b in btns:
            b.draw(screen, fonts['body'])

        pygame.display.flip()
        CLOCK.tick(60)


# =============================================================================
#                  PUZZLE 2 — EVENT QUEUE SIMULATOR (heap)
# =============================================================================

_EQ_HEAP_Y_BASE = _HEADER_H + 30
_EQ_HEAP_H      = 230
_EQ_PROCESS_Y   = _EQ_HEAP_Y_BASE + _EQ_HEAP_H + 5
_EQ_PROCESS_H   = 150

_EQ_NODE_R     = 18
_EQ_LEVEL_GAP  = 60
_EQ_TOP_MARGIN = _EQ_HEAP_Y_BASE + 25

_EQ_ARRIVAL_MEAN_S = 1.4
_EQ_SERVICE_MIN_S  = 0.8
_EQ_SERVICE_MAX_S  = 2.5

_EQ_PRIO_NAMES = [None, "Critical", "High", "Med", "Low", "Trivial"]


@dataclass(order=True)
class _EQEvent:
    priority:    int
    seq:         int
    label:       str   = field(compare=False)
    arrival_t:   float = field(compare=False, default=0.0)
    service_dur: float = field(compare=False, default=1.0)
    cx:          float = field(compare=False, default=WIDTH / 2)
    cy:          float = field(compare=False, default=-50.0)
    born_ms:     int   = field(compare=False, default=0)


def _eq_heap_pos(index, heap_size):
    level        = int(math.floor(math.log2(index + 1)))
    pos_in_level = index - (2 ** level - 1)
    count        = 2 ** level
    avail_w      = WIDTH - 60
    x = 30 + avail_w * (pos_in_level + 0.5) / count
    y = _EQ_TOP_MARGIN + level * _EQ_LEVEL_GAP
    return (x, y)


def _eq_lerp_xy(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _run_event_queue(fonts):
    screen = _screen()
    bg     = theme.make_background()

    state = {
        "running": True, "sim_time": 0.0, "sim_speed": 1.0,
        "seq": 0, "event_id": 0,
        "heap": [], "next_arrival_t": 0.5,
        "server": None, "server_start_t": 0.0,
        "processed": 0, "total_wait": 0.0,
        "history": [],
    }

    def next_id():
        state["event_id"] += 1
        return state["event_id"]

    def spawn(priority=None):
        if priority is None:
            priority = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 3, 2, 1])[0]
        state["seq"] += 1
        ev = _EQEvent(
            priority=priority,
            seq=state["seq"],
            label=f"E{next_id()}",
            arrival_t=state["sim_time"],
            service_dur=random.uniform(_EQ_SERVICE_MIN_S, _EQ_SERVICE_MAX_S),
            cx=WIDTH / 2 + random.uniform(-30, 30),
            cy=_EQ_HEAP_Y_BASE - 40,
            born_ms=pygame.time.get_ticks(),
        )
        heapq.heappush(state["heap"], ev)

    def schedule_next():
        state["next_arrival_t"] = state["sim_time"] + random.expovariate(1.0 / _EQ_ARRIVAL_MEAN_S)

    def reset():
        state.update({
            "running": True, "sim_time": 0.0, "sim_speed": 1.0,
            "seq": 0, "event_id": 0, "heap": [],
            "server": None, "server_start_t": 0.0,
            "processed": 0, "total_wait": 0.0, "history": [],
        })
        schedule_next()

    btns = [
        theme.Button((40,  555, 130, 36), "PAUSE / RESUME",
                     lambda: state.update(running=not state["running"]),
                     color=theme.WARNING),
        theme.Button((180, 555, 60,  36), "SLOW",
                     lambda: state.update(sim_speed=max(0.1, state["sim_speed"] / 1.4))),
        theme.Button((250, 555, 60,  36), "FAST",
                     lambda: state.update(sim_speed=min(8.0, state["sim_speed"] * 1.4))),
        theme.Button((320, 555, 90,  36), "INJECT",
                     lambda: spawn(priority=1), color=theme.DANGER),
        theme.Button((420, 555, 70,  36), "RESET", reset),
        theme.Button((WIDTH - 100, 555, 80, 36), "BACK",
                     lambda: state.update(_exit=True)),
    ]

    schedule_next()
    last_ms = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            for b in btns:
                b.handle(event)

        if state.get("_exit"):
            return "menu"

        now_ms  = pygame.time.get_ticks()
        dt_real = (now_ms - last_ms) / 1000.0
        last_ms = now_ms

        if state["running"]:
            state["sim_time"] += dt_real * state["sim_speed"]
            while state["sim_time"] >= state["next_arrival_t"]:
                spawn()
                schedule_next()
            if state["server"] is None and state["heap"]:
                state["server"]         = heapq.heappop(state["heap"])
                state["server_start_t"] = state["sim_time"]
                state["total_wait"]    += state["sim_time"] - state["server"].arrival_t
            elif state["server"] is not None:
                if state["sim_time"] - state["server_start_t"] >= state["server"].service_dur:
                    state["processed"] += 1
                    state["history"].insert(0, state["server"])
                    del state["history"][8:]
                    state["server"] = None

        # Animate node positions
        for i, ev in enumerate(state["heap"]):
            tx, ty = _eq_heap_pos(i, len(state["heap"]))
            ev.cx, ev.cy = _eq_lerp_xy((ev.cx, ev.cy), (tx, ty), 0.18)
        if state["server"]:
            target = (WIDTH / 2, _EQ_PROCESS_Y + _EQ_PROCESS_H / 2 - 18)
            state["server"].cx, state["server"].cy = _eq_lerp_xy(
                (state["server"].cx, state["server"].cy), target, 0.22)

        # Render
        screen.blit(bg, (0, 0))
        theme.draw_header(
            "Event Queue Simulator",
            "min-heap priority queue with discrete-event simulation   ESC: back",
            fonts,
        )

        # Heap panel
        pygame.draw.rect(screen, theme.PANEL_BG, (0, _EQ_HEAP_Y_BASE, WIDTH, _EQ_HEAP_H))
        screen.blit(fonts['small'].render("PRIORITY HEAP", True, theme.DIM),
                    (16, _EQ_HEAP_Y_BASE + 6))
        screen.blit(fonts['small'].render(f"size {len(state['heap'])}", True, theme.DIM),
                    (WIDTH - 90, _EQ_HEAP_Y_BASE + 6))

        # Edges parent -> child
        for i in range(1, len(state["heap"])):
            p = state["heap"][(i - 1) // 2]
            c = state["heap"][i]
            pygame.draw.line(screen, theme.EDGE_COL, (p.cx, p.cy), (c.cx, c.cy), 2)

        # Nodes
        for i, ev in enumerate(state["heap"]):
            color = theme.PRIO_COL[ev.priority]
            age   = now_ms - ev.born_ms
            pop_t = min(1.0, age / 220)
            r = int(_EQ_NODE_R * (0.4 + 0.6 * pop_t))
            pygame.draw.circle(screen, color, (int(ev.cx), int(ev.cy)), r)
            label = fonts['small'].render(ev.label, True, (20, 22, 35))
            screen.blit(label, (ev.cx - label.get_width() / 2,
                                ev.cy - label.get_height() / 2))
            if i == 0:
                pygame.draw.circle(screen, (255, 255, 255),
                                   (int(ev.cx), int(ev.cy)), r + 3, 2)

        # Server panel
        pygame.draw.line(screen, theme.PANEL_LINE,
                         (0, _EQ_PROCESS_Y), (WIDTH, _EQ_PROCESS_Y), 1)
        screen.blit(fonts['small'].render("SERVER", True, theme.DIM),
                    (16, _EQ_PROCESS_Y + 6))

        centre = (WIDTH / 2, _EQ_PROCESS_Y + _EQ_PROCESS_H / 2 - 18)
        pygame.draw.circle(screen, theme.PANEL_LINE,
                           (int(centre[0]), int(centre[1])), _EQ_NODE_R + 8, 2)

        if state["server"]:
            ev = state["server"]
            color = theme.PRIO_COL[ev.priority]
            pygame.draw.circle(screen, color, (int(ev.cx), int(ev.cy)), _EQ_NODE_R)
            label = fonts['small'].render(ev.label, True, (20, 22, 35))
            screen.blit(label, (ev.cx - label.get_width() / 2,
                                ev.cy - label.get_height() / 2))

            prog  = min(1.0, (state["sim_time"] - state["server_start_t"]) / ev.service_dur)
            bar_x = WIDTH / 2 - 150
            bar_y = _EQ_PROCESS_Y + _EQ_PROCESS_H / 2 + 14
            pygame.draw.rect(screen, theme.PANEL_LINE,
                             (bar_x, bar_y, 300, 6), border_radius=3)
            pygame.draw.rect(screen, color,
                             (bar_x, bar_y, 300 * prog, 6), border_radius=3)
            info = fonts['small'].render(
                f"{ev.label} | {_EQ_PRIO_NAMES[ev.priority]} | "
                f"waited {state['sim_time'] - ev.arrival_t:.1f}s",
                True, theme.TEXT,
            )
            screen.blit(info, (WIDTH / 2 - info.get_width() / 2, bar_y + 12))
        else:
            t = fonts['small'].render("idle - waiting for events", True, theme.DIM)
            screen.blit(t, (WIDTH / 2 - t.get_width() / 2,
                            _EQ_PROCESS_Y + _EQ_PROCESS_H / 2 + 14))

        # History dots
        screen.blit(fonts['small'].render("recent", True, theme.DIM),
                    (WIDTH - 230, _EQ_PROCESS_Y + 6))
        for i, ev in enumerate(state["history"]):
            cx2  = WIDTH - 24 - i * 26
            cy2  = _EQ_PROCESS_Y + 32
            alpha = max(60, 255 - i * 25)
            surf  = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*theme.PRIO_COL[ev.priority], alpha),
                               (11, 11), 9)
            screen.blit(surf, (cx2 - 11, cy2 - 11))

        # Status line (top-right)
        avg = state["total_wait"] / state["processed"] if state["processed"] else 0.0
        info = fonts['body'].render(
            f"t = {state['sim_time']:6.1f}s   processed {state['processed']}   "
            f"avg wait {avg:.2f}s   speed {state['sim_speed']:.1f}x"
            + ("   [PAUSED]" if not state["running"] else ""),
            True, theme.TEXT,
        )
        screen.blit(info, (WIDTH - info.get_width() - 16, _HEADER_H + 4))

        for b in btns:
            b.draw(screen, fonts['body'])

        pygame.display.flip()
        CLOCK.tick(60)


# =============================================================================
#                  PUZZLE 3 — DP GRID PATH COUNTER
# =============================================================================

_DP_CELL   = 42
_DP_COLS   = 14
_DP_ROWS   = 9
_DP_GRID_W = _DP_COLS * _DP_CELL
_DP_GRID_H = _DP_ROWS * _DP_CELL
_DP_GRID_X = (WIDTH - _DP_GRID_W) // 2
_DP_GRID_Y = _HEADER_H + 50

_DP_PAD    = 2
_DP_CORNER = 6
_DP_FILL_DELAY_MS = 35
_DP_PATH_DELAY_MS = 70


def _dp_compute(wall):
    """Standard 2-D path-count DP. Returns (table, fill_order, total)."""
    dp         = [[0] * _DP_COLS for _ in range(_DP_ROWS)]
    fill_order = []
    for r in range(_DP_ROWS):
        for c in range(_DP_COLS):
            fill_order.append((r, c))
            if wall[r][c]:
                continue
            if r == 0 and c == 0:
                dp[r][c] = 1
                continue
            v = 0
            if r > 0: v += dp[r - 1][c]
            if c > 0: v += dp[r][c - 1]
            dp[r][c] = v
    return dp, fill_order, dp[_DP_ROWS - 1][_DP_COLS - 1]


def _dp_sample_path(dp, wall):
    """Pick a random valid path, biased by sub-path counts."""
    if dp[_DP_ROWS - 1][_DP_COLS - 1] == 0:
        return []
    r, c = 0, 0
    path = [(0, 0)]
    while (r, c) != (_DP_ROWS - 1, _DP_COLS - 1):
        right = dp[r][c + 1] if (c + 1 < _DP_COLS and not wall[r][c + 1]) else 0
        down  = dp[r + 1][c] if (r + 1 < _DP_ROWS and not wall[r + 1][c]) else 0
        if right + down == 0:
            return path
        if random.random() < right / (right + down):
            c += 1
        else:
            r += 1
        path.append((r, c))
    return path


def _dp_format(n):
    if n < 1_000:         return str(n)
    if n < 1_000_000:     return f"{n / 1_000:.1f}k"
    if n < 1_000_000_000: return f"{n / 1_000_000:.1f}M"
    return f"{n:.1e}"


def _run_dp_grid(fonts):
    screen = _screen()
    bg     = theme.make_background()
    wall   = [[False] * _DP_COLS for _ in range(_DP_ROWS)]
    state  = {
        "dp": [[0] * _DP_COLS for _ in range(_DP_ROWS)],
        "fill_order": [], "fill_start_ms": 0,
        "mode": "EDIT", "total_paths": 0,
        "path": [], "path_start_ms": 0,
    }

    def start_fill():
        dp, order, total = _dp_compute(wall)
        state["dp"]            = dp
        state["fill_order"]    = order
        state["total_paths"]   = total
        state["fill_start_ms"] = pygame.time.get_ticks()
        state["mode"]          = "FILLING"
        state["path"]          = []

    def new_path():
        state["path"]          = _dp_sample_path(state["dp"], wall)
        state["path_start_ms"] = pygame.time.get_ticks()

    def reset_dp():
        state["dp"]          = [[0] * _DP_COLS for _ in range(_DP_ROWS)]
        state["mode"]        = "EDIT"
        state["path"]        = []
        state["total_paths"] = 0

    def clear_all():
        for r in range(_DP_ROWS):
            for c in range(_DP_COLS):
                wall[r][c] = False
        reset_dp()

    def toggle_wall(pos):
        if state["mode"] != "EDIT":
            return
        x, y = pos
        if not (_DP_GRID_X <= x < _DP_GRID_X + _DP_GRID_W and
                _DP_GRID_Y <= y < _DP_GRID_Y + _DP_GRID_H):
            return
        c = (x - _DP_GRID_X) // _DP_CELL
        r = (y - _DP_GRID_Y) // _DP_CELL
        if (r, c) == (0, 0) or (r, c) == (_DP_ROWS - 1, _DP_COLS - 1):
            return
        wall[r][c] = not wall[r][c]

    def space_action():
        if state["mode"] == "EDIT":
            start_fill()
        elif state["mode"] == "DONE" and state["total_paths"] > 0:
            new_path()

    btns = [
        theme.Button((40,  555, 140, 36), "RUN / NEW PATH",
                     space_action, color=theme.SUCCESS),
        theme.Button((190, 555, 100, 36), "RESET DP", reset_dp),
        theme.Button((300, 555, 80,  36), "CLEAR", clear_all, color=theme.DANGER),
        theme.Button((WIDTH - 100, 555, 80, 36), "BACK",
                     lambda: state.update(_exit=True)),
    ]

    dragging  = False
    last_cell = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "menu"
                if event.key == pygame.K_SPACE:  space_action()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                toggle_wall(event.pos)
                dragging = True
                x, y = event.pos
                if _DP_GRID_Y <= y < _DP_GRID_Y + _DP_GRID_H:
                    last_cell = ((y - _DP_GRID_Y) // _DP_CELL,
                                 (x - _DP_GRID_X) // _DP_CELL)
            if event.type == pygame.MOUSEBUTTONUP:
                dragging  = False
                last_cell = None
            if event.type == pygame.MOUSEMOTION and dragging and state["mode"] == "EDIT":
                x, y = event.pos
                if _DP_GRID_Y <= y < _DP_GRID_Y + _DP_GRID_H:
                    cell = ((y - _DP_GRID_Y) // _DP_CELL,
                            (x - _DP_GRID_X) // _DP_CELL)
                    if cell != last_cell:
                        toggle_wall(event.pos)
                        last_cell = cell
            for b in btns:
                b.handle(event)

        if state.get("_exit"):
            return "menu"

        now = pygame.time.get_ticks()

        # advance fill animation
        if state["mode"] == "FILLING":
            elapsed = now - state["fill_start_ms"]
            if elapsed >= len(state["fill_order"]) * _DP_FILL_DELAY_MS + 250:
                state["mode"] = "DONE"
                new_path()

        # Render
        screen.blit(bg, (0, 0))
        theme.draw_header(
            "DP Grid Path Counter",
            "click cells to toggle walls   SPACE: run or new path   ESC: back",
            fonts,
        )

        max_val = state["dp"][_DP_ROWS - 1][_DP_COLS - 1] if state["mode"] != "EDIT" else 0
        title_text = (f"total paths: {_dp_format(state['total_paths'])}"
                      if state["mode"] != "EDIT" else "place walls then press SPACE")
        screen.blit(fonts['body'].render(title_text, True, theme.TEXT),
                    (40, _HEADER_H + 15))

        path_idx = {cell: i for i, cell in enumerate(state["path"])}

        for r in range(_DP_ROWS):
            for c in range(_DP_COLS):
                rect = pygame.Rect(
                    _DP_GRID_X + c * _DP_CELL + _DP_PAD,
                    _DP_GRID_Y + r * _DP_CELL + _DP_PAD,
                    _DP_CELL - 2 * _DP_PAD,
                    _DP_CELL - 2 * _DP_PAD,
                )
                if wall[r][c]:
                    pygame.draw.rect(screen, theme.WALL_COL, rect, border_radius=_DP_CORNER)
                    continue

                if state["mode"] != "EDIT" and max_val > 0:
                    t = math.log1p(state["dp"][r][c]) / math.log1p(max_val)
                    base = theme.lerp(theme.EMPTY_COL, (125, 170, 247), t)
                else:
                    base = theme.EMPTY_COL

                if state["mode"] == "FILLING":
                    elapsed  = now - state["fill_start_ms"]
                    idx      = r * _DP_COLS + c
                    reveal_t = (elapsed - idx * _DP_FILL_DELAY_MS) / 250
                    reveal   = max(0.0, min(1.0, reveal_t))
                    base     = theme.lerp(theme.EMPTY_COL, base, reveal)

                if (r, c) in path_idx:
                    p_idx     = path_idx[(r, c)]
                    p_elapsed = now - state["path_start_ms"]
                    if p_idx * _DP_PATH_DELAY_MS <= p_elapsed:
                        pulse  = (math.sin(now / 280 + p_idx * 0.25) + 1) * 0.5
                        path_c = theme.lerp(theme.PATH_COL, theme.PATH_GLOW, pulse * 0.4)
                        base   = theme.lerp(base, path_c, 0.85)

                if (r, c) == (0, 0):
                    pulse = (math.sin(now / 280) + 1) * 0.5
                    base  = theme.lerp(base, theme.lerp(
                        theme.START_COL, theme.START_GLOW, pulse * 0.5), 0.9)
                elif (r, c) == (_DP_ROWS - 1, _DP_COLS - 1):
                    pulse = (math.sin(now / 280 + 1.5) + 1) * 0.5
                    base  = theme.lerp(base, theme.lerp(
                        theme.END_COL, theme.END_GLOW, pulse * 0.5), 0.9)

                pygame.draw.rect(screen, base, rect, border_radius=_DP_CORNER)

                if state["mode"] != "EDIT" and state["dp"][r][c] > 0:
                    text = _dp_format(state["dp"][r][c])
                    t    = fonts['small'].render(text, True, theme.TEXT)
                    screen.blit(t, (
                        rect.centerx - t.get_width()  / 2,
                        rect.centery - t.get_height() / 2,
                    ))

        for b in btns:
            b.draw(screen, fonts['body'])

        pygame.display.flip()
        CLOCK.tick(60)


# =============================================================================
#                       TOP-LEVEL PICKER + ENTRY POINT
# =============================================================================

def _run_picker(fonts):
    """Cards-style picker. Click one to enter that puzzle. ESC to exit."""
    screen = _screen()
    bg     = theme.make_background()

    choice = {"value": None}

    def pick_path():   choice["value"] = "pathfinding"
    def pick_event():  choice["value"] = "event_queue"
    def pick_dp():     choice["value"] = "dp_grid"

    card_w, card_h = 220, 280
    gap            = 30
    total_w        = card_w * 3 + gap * 2
    start_x        = (WIDTH - total_w) // 2
    card_y         = _HEADER_H + 90

    cards = [
        ("Pathfinding", "A* search with",   "interactive walls",  pick_path),
        ("Event Queue", "Priority heap +",  "discrete-event sim", pick_event),
        ("DP Grid",     "Count paths with", "dynamic programming",pick_dp),
    ]
    card_rects = [
        pygame.Rect(start_x + i * (card_w + gap), card_y, card_w, card_h)
        for i in range(3)
    ]

    btn_back = theme.Button(
        (WIDTH - 100, HEIGHT - 50, 80, 36), "BACK",
        lambda: choice.update(value="exit"),
    )

    while choice["value"] is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, (_, _, _, callback) in zip(card_rects, cards):
                    if rect.collidepoint(event.pos):
                        callback()
                        break
            btn_back.handle(event)

        now = pygame.time.get_ticks()
        screen.blit(bg, (0, 0))
        theme.draw_header(
            "Puzzles",
            "pick a visualiser   ESC to return to main menu",
            fonts,
        )

        mouse_pos = pygame.mouse.get_pos()
        for rect, (title, line1, line2, _) in zip(card_rects, cards):
            hovered = rect.collidepoint(mouse_pos)
            pulse   = (math.sin(now / 600) + 1) * 0.5
            base    = theme.lerp(theme.PANEL_BG, (235, 240, 255), pulse * 0.6)
            if hovered:
                base = theme.lerp(base, (255, 255, 255), 0.5)
            pygame.draw.rect(screen, base, rect, border_radius=12)
            pygame.draw.rect(screen, theme.PANEL_LINE, rect, width=2, border_radius=12)

            t_title = fonts['title'].render(title, True, theme.TEXT)
            screen.blit(t_title, (rect.centerx - t_title.get_width() // 2, rect.y + 30))
            t_line1 = fonts['body'].render(line1, True, theme.DIM)
            t_line2 = fonts['body'].render(line2, True, theme.DIM)
            screen.blit(t_line1, (rect.centerx - t_line1.get_width() // 2, rect.y + 120))
            screen.blit(t_line2, (rect.centerx - t_line2.get_width() // 2, rect.y + 150))

            t_hint = fonts['small'].render("click to open", True,
                                           theme.SUCCESS if hovered else theme.DIM)
            screen.blit(t_hint, (rect.centerx - t_hint.get_width() // 2, rect.y + 230))

        btn_back.draw(screen, fonts['body'])

        pygame.display.flip()
        CLOCK.tick(60)

    return choice["value"]


def puzzles_module() -> None:
    """
    Entry point used by `cores/setup.py`:
        from modules.puzzles import puzzles_module
        puzzles_module()

    Flow:  main menu --> picker --> sub-puzzle --(ESC)--> main menu
    """
    fonts  = _build_fonts()
    choice = _run_picker(fonts)

    if choice in ("exit", None):
        return
    if choice == "quit":
        pygame.quit()
        exit()

    if   choice == "pathfinding": result = _run_pathfinding(fonts)
    elif choice == "event_queue": result = _run_event_queue(fonts)
    elif choice == "dp_grid":     result = _run_dp_grid(fonts)
    else:                          result = "menu"

    if result == "quit":
        pygame.quit()
        exit()
    # ESC in a sub-puzzle returns straight to the main menu (single key press).