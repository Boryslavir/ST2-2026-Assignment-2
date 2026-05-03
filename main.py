import pygame
import sys

from pygame.font import Font
from pygame.time import Clock


# Constants
WIDTH:              int                     = 800
HEIGHT:             int                     = 600
BACKGROUND_COLOR:   tuple[int, int, int]    = (200, 200, 250)
BUTTON_COLOR:       tuple[int, int, int]    = (150, 150, 200)
TEXT_COLOR:         tuple[int, int, int]    = (0, 0, 0)


# Initialize Pygame
pygame.init()

screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Algorithm Explorer")

FONT: Font = pygame.font.SysFont(None, 36)
clock: Clock = pygame.time.Clock()


def draw_text(text, pos):
    """Render and draw text on screen"""
    txt = FONT.render(text, True, TEXT_COLOR)
    screen.blit(txt, pos)


def create_buttons():
    """Create main menu buttons"""
    return {
        'Data Structures': pygame.Rect(300, 150, 200, 50),
        'Sorting': pygame.Rect(300, 230, 200, 50),
        'Graphs': pygame.Rect(300, 310, 200, 50),
        'Heap': pygame.Rect(300, 390, 200, 50),
        'Puzzles': pygame.Rect(300, 470, 200, 50),
    }


def main_menu():
    """Draw the main menu screen"""
    screen.fill(BACKGROUND_COLOR)
    draw_text("Algorithm Explorer", (WIDTH // 3, 50))

    buttons = create_buttons()
    for text, rect in buttons.items():
        pygame.draw.rect(screen, BUTTON_COLOR, rect)
        draw_text(text, (rect.x + 20, rect.y + 10))

    pygame.display.flip()
    return buttons


# Module placeholder functions
def data_structures_module():
    """Stack, queue, linked list, BST visualization"""
    # TODO: Implement data structures visualization
    pass


def sorting_module():
    """Bubble sort, selection sort, merge sort visualizations"""
    # TODO: Implement sorting visualizations
    pass


def graphs_module():
    """BFS, DFS visualization with interactive graph"""
    # TODO: Implement graph algorithms visualization
    pass


def heap_module():
    """Heap insertion and extraction visualization"""
    # TODO: Implement heap operations visualization
    pass


def puzzles_module():
    """Pathfinding, event simulation, DP puzzles"""
    # TODO: Implement puzzle games
    pass


def handle_module_selection(module_name):
    """Route to the selected module"""
    modules = {
        'Data Structures': data_structures_module,
        'Sorting': sorting_module,
        'Graphs': graphs_module,
        'Heap': heap_module,
        'Puzzles': puzzles_module,
    }

    if module_name in modules:
        modules[module_name]()
    return None  # Return to main menu after module completion


def main():
    """Main game loop"""
    running:        bool        = True
    current_module: str | None  = None

    buttons = main_menu()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and current_module is None:
                pos = event.pos
                for name, rect in buttons.items():
                    if rect.collidepoint(pos):
                        current_module = name
                        break

        # Handle module execution
        if current_module is not None:
            current_module = handle_module_selection(current_module)
            if current_module is None:  # Return to menu
                buttons = main_menu()

        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
