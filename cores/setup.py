import pygame


# Initialize Pygame
# NOTE: this has to be done first before importing other constants
pygame.init()


from cores.globals import (
    WIDTH,
    HEIGHT,
    BG_COLOUR,
    BTN_COLOUR,
    TXT_COLOUR,
    FONT,
    CLOCK
)
from typing import Any


# Setup Pygame display screen
screen: pygame.Surface = pygame.display.set_mode(
    size=(WIDTH, HEIGHT),
    flags=pygame.SHOWN | pygame.RESIZABLE
)
pygame.display.set_caption(title="Algorithm Explorer")


def draw_text(
    text: str,
    pos: tuple[int | float, int | float]
) -> None:
    """Render and draw text on screen"""
    txt: pygame.Surface = FONT.render(
        text,
        True,
        TXT_COLOUR
    )
    screen.blit(
        source=txt,
        dest=pos
    )

    return None


def main_menu() -> dict[str, pygame.Rect]:
    """Draw the main menu screen"""
    screen.fill(color=BG_COLOUR)
    draw_text(
        text="Algorithm Explorer",
        pos=(WIDTH // 3, 50)
    )

    buttons: dict[str, pygame.Rect] = {
        'Data Structures':  pygame.Rect(300, 150, 200, 50),
        'Sorting':          pygame.Rect(300, 230, 200, 50),
        'Graphs':           pygame.Rect(300, 310, 200, 50),
        'Heap':             pygame.Rect(300, 390, 200, 50),
        'Puzzles':          pygame.Rect(300, 470, 200, 50),
    }

    for (text, rect) in buttons.items():
        # NOTE: these 2 vars are for type-hint purposes only
        text: str
        rect: pygame.Rect

        pygame.draw.rect(
            surface=screen,
            color=BTN_COLOUR,
            rect=rect
        )
        draw_text(
            text=text,
            pos=(rect.x + 20, rect.y + 10)
        )

    pygame.display.flip()

    return buttons


def main():
    """Main game loop"""
    running:        bool        = True
    current_module: str | None  = None

    buttons: dict[str, pygame.Rect] = main_menu()

    while running:
        for event in pygame.event.get():
            # NOTE: this var is for type-hint purposes only
            event: pygame.event.Event

            if event.type == pygame.QUIT:
                running = False

            elif (event.type == pygame.MOUSEBUTTONDOWN) \
            and  (current_module is None):
                pos: tuple[Any] = event.pos

                for (name, rect) in buttons.items():
                    # NOTE: these 2 vars are for type-hint purposes only
                    name: str
                    rect: pygame.Rect

                    if rect.collidepoint(pos):
                        current_module = name
                        break

        if current_module is None:
            # Return to main menu
            buttons: dict[str, pygame.Rect] = main_menu()

        else:
            # Modular DSA selection buttons
            match current_module:
                case 'Data Structures':
                    from modules.data_structures import data_structures_module

                    data_structures_module()

                case 'Sorting':
                    from modules.sorting import sorting_module

                    sorting_module()

                case 'Graphs':
                    from modules.graphs import graphs_module

                    graphs_module()

                case 'Heap':
                    from modules.heap import heap_module

                    heap_module()

                case 'Puzzles':
                    from modules.puzzles import puzzles_module

                    puzzles_module()

        CLOCK.tick(30.0)

    pygame.quit()
