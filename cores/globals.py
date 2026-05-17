from pygame.font import SysFont, Font
from pygame.time import Clock


# Constants
WIDTH:      int                     = 800
HEIGHT:     int                     = 600
BG_COLOUR:  tuple[int, int, int]    = (200, 200, 250)
BTN_COLOUR: tuple[int, int, int]    = (150, 150, 200)
TXT_COLOUR: tuple[int, int, int]    = (0, 0, 0)
FONT:       Font                    = SysFont(name=None, size=36)
CLOCK:      Clock                   = Clock()


# ============================================================================ #
#                                   Phase 3 only                               #
# ============================================================================ #
HEADER_HEIGHT:      int                     = 60
TEXT:               tuple[int, int, int]    = (35, 35, 50)
DIM :               tuple[int, int, int]    = (110, 110, 130)
EMPTY_COLOUR:       tuple[int, int, int]    = (235, 235, 248)
WALL_COLOUR:        tuple[int, int, int]    = (60, 60, 80)
START_COLOUR:       tuple[int, int, int]    = (80, 200, 120)
START_GLOW:         tuple[int, int, int]    = (180, 250, 200)
END_COLOUR:         tuple[int, int, int]    = (240, 80, 80)
END_GLOW:           tuple[int, int, int]    = (255, 180, 180)
PATH_COLOUR:        tuple[int, int, int]    = (240, 200, 50)
PATH_GLOW:          tuple[int, int, int]    = (255, 245, 200)
FRONTIER_COLOUR:    tuple[int, int, int]    = (250, 220, 100)
VISITED_COLOUR:     tuple[int, int, int]    = (140, 200, 240)
EDGE_COLOUR:        tuple[int, int, int]    = (160, 160, 180)
BG_PANEL:           tuple[int, int, int]    = (220, 220, 240)
LINE_PANEL:         tuple[int, int, int]    = (150, 150, 180)
TXT_SUCCESS:        tuple[int, int, int]    = (90, 200, 130)
TXT_DANGER:         tuple[int, int, int]    = (230, 100, 100)
TXT_WARNING:        tuple[int, int, int]    = (240, 200, 80)
PRIO_COLOUR:        list[tuple[int, int, int]] = [
    (0, 0, 0),
    (230, 80, 80),
    (240, 150, 80),
    (240, 220, 100),
    (100, 200, 150),
    (120, 170, 220)
]

# Puzzle 1
PF_CELL:                int = 22
PF_COLS:                int = 28
PF_ROWS:                int = 17
PF_GRID_W:              int = PF_COLS * PF_CELL
PF_GRID_H:              int = PF_ROWS * PF_CELL
PF_GRID_X:              int = (WIDTH - PF_GRID_W) // 2
PF_GRID_Y:              int = HEADER_HEIGHT + 50
PF_PAD:                 int = 2
PF_CORNER:              int = 4
PF_FADE_MS:             int = 280
PF_PATH_REVEAL_MS:      int = 22
PF_STEPS_PER_FRAME:     int = 2
