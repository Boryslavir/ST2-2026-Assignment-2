import pygame
import sys

from pygame.font import Font
from pygame.time import Clock

WIDTH, HEIGHT = 800, 600
NODE_W, NODE_H = 120, 40
GAP = 10

FONT = pygame.font.SysFont(None, 32)

def draw_text(surface, text, pos, color=(0,0,0)):
    surface.blit(FONT.render(text, True, color), pos)

def stack_visualiser(screen):
    stack = []
    input_value = ""
    running = True

    while running:
        screen.fill((230, 230, 255))

        draw_text(screen, "STACK VISUALISER (ESC to return)", (220, 20))

        # Draw input box
        pygame.draw.rect(screen, (255,255,255), (300, 80, 200, 40))
        draw_text(screen, input_value, (310, 85))

        # Buttons
        push_btn = pygame.Rect(250, 140, 120, 40)
        pop_btn  = pygame.Rect(430, 140, 120, 40)

        pygame.draw.rect(screen, (180,180,250), push_btn)
        pygame.draw.rect(screen, (250,180,180), pop_btn)

        draw_text(screen, "PUSH", (push_btn.x+25, push_btn.y+8))
        draw_text(screen, "POP", (pop_btn.x+35, pop_btn.y+8))

        # Draw stack
        y = HEIGHT - 80
        for value in reversed(stack):
            pygame.draw.rect(screen, (150,200,255), (340, y, NODE_W, NODE_H))
            draw_text(screen, str(value), (380, y+8))
            y -= NODE_H + GAP

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_BACKSPACE:
                    input_value = input_value[:-1]
                elif event.unicode.isdigit():
                    input_value += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if push_btn.collidepoint(event.pos) and input_value:
                    stack.append(int(input_value))
                    input_value = ""
                if pop_btn.collidepoint(event.pos) and stack:
                    stack.pop()
