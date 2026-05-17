import pygame


# Pygame General Constants
WIDTH:      int                     = 800
HEIGHT:     int                     = 600
BTN_COLOUR: tuple[int, int, int]    = (150, 150, 200)   # RGB format
TXT_COLOUR: tuple[int, int, int]    = (0, 0, 0)         # RGB format
CLOCK:      pygame.time.Clock       = pygame.time.Clock()


# PyGame Fonts
FONT:       pygame.font.Font = pygame.font.SysFont(name=None,size=36)
FONT_SM:    pygame.font.Font = pygame.font.SysFont(name=None,size=26)
FONT_TITLE: pygame.font.Font = pygame.font.SysFont(name=None,size=48)


# PyGame Palette (RGB format)
BG_COLOUR:      tuple[int, int, int] = (200, 200, 250)
PANEL_COLOUR:   tuple[int, int, int] = (150, 150, 200)
DARK:           tuple[int, int, int] = (0, 0, 0)
WHITE:          tuple[int, int, int] = (255, 255, 255)



# ============================================================================ #
#                                   Phase 2 only                               #
# ============================================================================ #
BAR_DEFAULT:    tuple[int, int, int] = (100, 140, 220)
BAR_COMPARE:    tuple[int, int, int] = (240, 80, 80)
BAR_SORTED:     tuple[int, int, int] = (80, 200, 120)
BAR_PIVOT:      tuple[int, int, int] = (240, 200, 50)
EDGE_COLOUR:    tuple[int, int, int] = (60, 60, 60)
NODE_DEFAULT:   tuple[int, int, int] = (100, 140, 220)
NODE_VISITED:   tuple[int, int, int] = (80, 200, 120)
NODE_CURRENT:   tuple[int, int, int] = (240, 80, 80)
NODE_QUEUED:    tuple[int, int, int] = (240, 200, 50)
HEAP_NODE:      tuple[int, int, int] = (100, 140, 220)
HEAP_HIGHLIGHT: tuple[int, int, int] = (240, 80, 80)
BG_TOOLBAR:     tuple[int, int, int] = (230, 230, 255)


# Shared pygame surface
SCREEN: pygame.Surface = pygame.display.set_mode(
    size=(WIDTH, HEIGHT),
    flags=pygame.SHOWN | pygame.RESIZABLE,
)



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

# Puzzle 2
EQ_HEAP_Y_BASE:     int     = HEADER_HEIGHT + 30
EQ_HEAP_H:          int     = 230
EQ_PROCESS_Y:       int     = EQ_HEAP_Y_BASE + EQ_HEAP_H + 5
EQ_PROCESS_H:       int     = 150
EQ_NODE_R:          int     = 18
EQ_LEVEL_GAP:       int     = 60
EQ_TOP_MARGIN:      int     = EQ_HEAP_Y_BASE + 25
EQ_ARRIVAL_MEAN_S:  float   = 1.4
EQ_SERVICE_MIN_S:   float   = 0.8
EQ_SERVICE_MAX_S:   float   = 2.5
EQ_PRIO_NAMES:      list[str | None] = [
    None,
    "Critical",
    "High",
    "Med",
    "Low",
    "Trivial"
]

# Puzzle 3
DP_CELL:            int = 42
DP_COLS:            int = 14
DP_ROWS:            int = 9
DP_GRID_W:          int = DP_COLS * DP_CELL
DP_GRID_H:          int = DP_ROWS * DP_CELL
DP_GRID_X:          int = (WIDTH - DP_GRID_W) // 2
DP_GRID_Y:          int = HEADER_HEIGHT + 50
DP_PAD:             int = 2
DP_CORNER:          int = 6
DP_FILL_DELAY_MS:   int = 35
DP_PATH_DELAY_MS:   int = 70
