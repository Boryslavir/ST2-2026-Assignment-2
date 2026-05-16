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
