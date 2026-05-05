import pygame
import sys

WIDTH, HEIGHT = 800, 600
NODE_W, NODE_H = 100, 40
GAP = 40

def draw_text(surface, text, pos, font, color=(0,0,0)):
    surface.blit(font.render(text, True, color), pos)

def linked_list_visualiser(screen): 
    linked_list = []
    input_value = ""
    running = True

    FONT = pygame.font.SysFont(None, 32)

    while running:
        screen.fill((220, 255, 240))

        draw_text(screen, "LINKED LIST VISUALISER (ESC to return)", (200, 20), FONT)

        pygame.draw.rect(screen, (255,255,255), (300, 80, 200, 40))
        draw_text(screen, input_value, (310, 85), FONT)

        insert_btn = pygame.Rect(150, 140, 120, 40)
        delete_btn = pygame.Rect(330, 140, 120, 40)
        reverse_btn = pygame.Rect(510, 140, 120, 40)

        pygame.draw.rect(screen, (180,250,180), insert_btn)
        pygame.draw.rect(screen, (250,180,180), delete_btn)
        pygame.draw.rect(screen, (180,180,250), reverse_btn)

        draw_text(screen, "INSERT", (insert_btn.x+25, insert_btn.y+8), FONT)
        draw_text(screen, "DELETE", (delete_btn.x+25, delete_btn.y+8), FONT)
        draw_text(screen, "REVERSE", (reverse_btn.x+15, reverse_btn.y+8), FONT)

        # Draw linked list
        x = 80
        y = 300
        for value in linked_list:
            pygame.draw.rect(screen, (200,255,255), (x, y, NODE_W, NODE_H))
            draw_text(screen, str(value), (x+35, y+8), FONT)
            pygame.draw.line(screen, (0,0,0), (x+NODE_W, y+NODE_H//2), (x+NODE_W+GAP, y+NODE_H//2), 3)
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
                if insert_btn.collidepoint(event.pos) and input_value:
                    linked_list.append(int(input_value))
                    input_value = ""

                if delete_btn.collidepoint(event.pos) and input_value:
                    val = int(input_value)
                    if val in linked_list:
                        linked_list.remove(val)
                    input_value = ""

                if reverse_btn.collidepoint(event.pos):
                    linked_list.reverse()

