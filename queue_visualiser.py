import pygame
import sys

WIDTH, HEIGHT = 800, 600
NODE_W, NODE_H = 120, 40
GAP = 20

FONT = pygame.font.SysFont(None, 32)

def draw_text(surface, text, pos, color=(0,0,0)):
    surface.blit(FONT.render(text, True, color), pos)

def queue_visualiser(screen):
    queue = []
    input_value = ""
    running = True

    while running:
        screen.fill((255, 240, 220))

        draw_text(screen, "QUEUE VISUALISER (ESC to return)", (220, 20))

        pygame.draw.rect(screen, (255,255,255), (300, 80, 200, 40))
        draw_text(screen, input_value, (310, 85))

        enqueue_btn = pygame.Rect(250, 140, 140, 40)
        dequeue_btn = pygame.Rect(430, 140, 140, 40)

        pygame.draw.rect(screen, (180,250,180), enqueue_btn)
        pygame.draw.rect(screen, (250,180,180), dequeue_btn)

        draw_text(screen, "ENQUEUE", (enqueue_btn.x+15, enqueue_btn.y+8))
        draw_text(screen, "DEQUEUE", (dequeue_btn.x+15, dequeue_btn.y+8))

        # Draw queue horizontally
        x = 100
        y = 300
        for value in queue:
            pygame.draw.rect(screen, (200,200,255), (x, y, NODE_W, NODE_H))
            draw_text(screen, str(value), (x+40, y+8))
            x += NODE_W + GAP

        pygame.display.flip()

        # Events
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
                if enqueue_btn.collidepoint(event.pos) and input_value:
                    queue.append(int(input_value))
                    input_value = ""
                if dequeue_btn.collidepoint(event.pos) and queue:
                    queue.pop(0)
