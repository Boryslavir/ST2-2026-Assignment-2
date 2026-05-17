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
