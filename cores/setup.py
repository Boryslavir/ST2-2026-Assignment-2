# NOTE: pygame.init() must run before globals imports SCREEN / fonts
import pygame
pygame.init()


from cores.globals import (
    BG_COLOUR,
    BG_TOOLBAR,
    BTN_COLOUR,
    CLOCK,
    DARK,
    FONT,
    FONT_SM,
    HEIGHT,
    PANEL_COLOUR,
    SCREEN,
    WIDTH
)
from time import time
from sys import exit
from typing import Any


pygame.display.set_caption("Algorithm Explorer")


# Shared helper functions
def draw_text(
    text:    str,
    pos:     tuple[int, int],
    font:    pygame.font.Font | None        = None,
    colour:  tuple[int, int, int]           = DARK,
    surface: pygame.surface.Surface | None  = None,
) -> None:
    """Render `text` at `pos` on `surface` (defaults to SCREEN)."""
    if font is None:
        font = FONT

    if surface is None:
        surface = SCREEN

    surface.blit(font.render(text, True, colour), pos)


def draw_toolbar(
    instructions: str,
    status: str = "",
) -> None:
    """Draw the common instructions / status strip along the bottom edge."""
    rect: pygame.Rect = pygame.Rect(0, HEIGHT - 60, WIDTH, 60)
    pygame.draw.rect(surface=SCREEN, color=BG_TOOLBAR, rect=rect)
    pygame.draw.line(
        surface=SCREEN,
        color=PANEL_COLOUR,
        start_pos=(0,     HEIGHT - 60),
        end_pos=  (WIDTH, HEIGHT - 60),
        width=2,
    )
    draw_text(text=instructions, pos=(10, HEIGHT - 50), font=FONT_SM, colour=DARK)
    if status:
        draw_text(text=status, pos=(10, HEIGHT - 28), font=FONT_SM, colour=(60, 60, 160))


def make_button(label: str, rect: pygame.Rect) -> pygame.Rect:
    """Draw a labelled button and return its rect (for hit-testing)."""
    pygame.draw.rect(surface=SCREEN, color=PANEL_COLOUR, rect=rect, border_radius=6)
    pygame.draw.rect(surface=SCREEN, color=DARK,         rect=rect, width=2, border_radius=6)
    text_width: int = FONT_SM.size(label)[0]
    draw_text(
        text=label,
        pos=(rect.x + (rect.width - text_width) // 2, rect.y + 8),
        font=FONT_SM,
    )
    return rect


def wait_or_skip(delay: float) -> bool:
    """
    Block for `delay` seconds while pumping the event queue.
    Returns True if the user pressed ESC or closed the window (abort signal).
    """
    start: float = time()
    while (time() - start) < delay:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
        CLOCK.tick(60)
    return False


def main_menu() -> dict[str, pygame.Rect]:
    """Draw the main menu screen and return button rects."""
    SCREEN.fill(color=BG_COLOUR)
    draw_text(text="Algorithm Explorer", pos=(WIDTH // 3, 50))

    buttons: dict[str, pygame.Rect] = {
        'Data Structures':  pygame.Rect(300, 150, 200, 50),
        'Sorting':          pygame.Rect(300, 230, 200, 50),
        'Graphs':           pygame.Rect(300, 310, 200, 50),
        'Heap':             pygame.Rect(300, 390, 200, 50),
        'Puzzles':          pygame.Rect(300, 470, 200, 50),
    }

    for text, rect in buttons.items():
        pygame.draw.rect(surface=SCREEN, color=BTN_COLOUR, rect=rect)
        draw_text(text=text, pos=(rect.x + 20, rect.y + 10))

    pygame.display.flip()
    return buttons


# Core entry point
def main() -> None:
    """Main game loop."""
    running:        bool            = True
    current_module: str | None      = None
    buttons:        dict[str, pygame.Rect] = {}


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and current_module is None:
                pos: tuple[Any, ...] = event.pos
                for name, rect in buttons.items():
                    if rect.collidepoint(pos):
                        current_module = name
                        break

        if current_module is None:
            buttons = main_menu()
        else:
            match current_module:
                case 'Data Structures':
                    from modules.data_structures import data_structures_module
                    data_structures_module()

                case 'Sorting':
                    from modules.sorting import SortingModule
                    sorting_mod: SortingModule = SortingModule()
                    sorting_mod.run()

                case 'Graphs':
                    from modules.graphs import GraphModule
                    graph_mod: GraphModule = GraphModule()
                    graph_mod.run()

                case 'Heap':
                    from modules.heap import HeapModule
                    heap_mod: HeapModule = HeapModule()
                    heap_mod.run()

                case 'Puzzles':
                    from modules.puzzles import puzzles_module
                    puzzles_module()

                case _:
                    pass

            # Module returned (ESC pressed) — go back to menu
            current_module = None

        CLOCK.tick(30)

    pygame.quit()
    exit()
