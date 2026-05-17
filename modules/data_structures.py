import pygame
from sys import exit
from cores.globals import (
    FONT,
    HEIGHT,
    WIDTH
)



def data_structures_module(screen):
    def draw_text(surface, text, pos, font=FONT, color=(0,0,0)):
        surface.blit(font.render(text, True, color), pos)

    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

    def insert(root, value):
        if root is None:
            return Node(value)
        if value < root.value:
            root.left = insert(root.left, value)
        else:
            root.right = insert(root.right, value)
        return root

    def draw_tree(surface, node, x, y, dx, font):
        if node is None:
            return
        pygame.draw.circle(surface, (180,200,255), (x, y), 25)
        draw_text(surface, str(node.value), (x-10, y-10), font)

        if node.left:
            pygame.draw.line(surface, (0,0,0), (x, y), (x-dx, y+80), 3)
            draw_tree(surface, node.left, x-dx, y+80, dx//2, font)

        if node.right:
            pygame.draw.line(surface, (0,0,0), (x, y), (x+dx, y+80), 3)
            draw_tree(surface, node.right, x+dx, y+80, dx//2, font)

    def inorder(node):
        if not node: return ""
        return inorder(node.left) + f"{node.value} " + inorder(node.right)

    def preorder(node):
        if not node: return ""
        return f"{node.value} " + preorder(node.left) + preorder(node.right)

    def postorder(node):
        if not node: return ""
        return postorder(node.left) + postorder(node.right) + f"{node.value} "

    def bst_visualiser(surface):
        FONT2 = pygame.font.SysFont(None, 28)
        root = None
        input_value = ""
        traversal_text = ""
        running = True

        while running:
            surface.fill((255, 240, 255))
            draw_text(surface, "BST VISUALISER (ESC to return)", (250, 20), FONT2)

            pygame.draw.rect(surface, (255,255,255), (300, 80, 200, 40))
            draw_text(surface, input_value, (310, 85), FONT2)

            insert_btn = pygame.Rect(350, 140, 120, 40)
            inorder_btn = pygame.Rect(150, 500, 120, 40)
            preorder_btn = pygame.Rect(330, 500, 120, 40)
            postorder_btn = pygame.Rect(510, 500, 120, 40)

            pygame.draw.rect(surface, (180,250,180), insert_btn)
            pygame.draw.rect(surface, (200,200,255), inorder_btn)
            pygame.draw.rect(surface, (200,200,255), preorder_btn)
            pygame.draw.rect(surface, (200,200,255), postorder_btn)

            draw_text(surface, "INSERT", (insert_btn.x+25, insert_btn.y+8), FONT2)
            draw_text(surface, "INORDER", (inorder_btn.x+15, inorder_btn.y+8), FONT2)
            draw_text(surface, "PREORDER", (preorder_btn.x+5, preorder_btn.y+8), FONT2)
            draw_text(surface, "POSTORDER", (postorder_btn.x+5, postorder_btn.y+8), FONT2)

            draw_tree(surface, root, WIDTH // 2, 200, 200, FONT2)
            draw_text(surface, traversal_text, (50, 450), FONT2)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_BACKSPACE:
                        input_value = input_value[:-1]
                    elif event.unicode.isdigit():
                        input_value += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if insert_btn.collidepoint(event.pos) and input_value:
                        root = insert(root, int(input_value))
                        input_value = ""

                    if inorder_btn.collidepoint(event.pos):
                        traversal_text = "Inorder: " + inorder(root)

                    if preorder_btn.collidepoint(event.pos):
                        traversal_text = "Preorder: " + preorder(root)

                    if postorder_btn.collidepoint(event.pos):
                        traversal_text = "Postorder: " + postorder(root)

    def linked_list_visualiser(surface):
        linked_list = []
        input_value = ""
        running = True
        FONT2 = pygame.font.SysFont(None, 32)

        while running:
            surface.fill((220, 255, 240))
            draw_text(surface, "LINKED LIST VISUALISER (ESC to return)", (200, 20), FONT2)

            pygame.draw.rect(surface, (255,255,255), (300, 80, 200, 40))
            draw_text(surface, input_value, (310, 85), FONT2)

            insert_btn = pygame.Rect(150, 140, 120, 40)
            delete_btn = pygame.Rect(330, 140, 120, 40)
            reverse_btn = pygame.Rect(510, 140, 120, 40)

            pygame.draw.rect(surface, (180,250,180), insert_btn)
            pygame.draw.rect(surface, (250,180,180), delete_btn)
            pygame.draw.rect(surface, (180,180,250), reverse_btn)

            draw_text(surface, "INSERT", (insert_btn.x+25, insert_btn.y+8), FONT2)
            draw_text(surface, "DELETE", (delete_btn.x+25, delete_btn.y+8), FONT2)
            draw_text(surface, "REVERSE", (reverse_btn.x+15, reverse_btn.y+8), FONT2)

            x = 80
            y = 300

            for value in linked_list:
                pygame.draw.rect(surface, (200,255,255), (x, y, 100, 40))
                draw_text(surface, str(value), (x+35, y+8), FONT2)
                pygame.draw.line(surface, (0,0,0), (x+100, y+20), (x+140, y+20), 3)
                x += 140

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

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

    def queue_visualiser(surface):
        queue = []
        input_value = ""
        running = True

        while running:
            surface.fill((255, 240, 220))
            draw_text(surface, "QUEUE VISUALISER (ESC to return)", (220, 20))

            pygame.draw.rect(surface, (255,255,255), (300, 80, 200, 40))
            draw_text(surface, input_value, (310, 85))

            enqueue_btn = pygame.Rect(250, 140, 140, 40)
            dequeue_btn = pygame.Rect(430, 140, 140, 40)

            pygame.draw.rect(surface, (180,250,180), enqueue_btn)
            pygame.draw.rect(surface, (250,180,180), dequeue_btn)

            draw_text(surface, "ENQUEUE", (enqueue_btn.x+15, enqueue_btn.y+8))
            draw_text(surface, "DEQUEUE", (dequeue_btn.x+15, dequeue_btn.y+8))

            x = 100
            y = 300

            for value in queue:
                pygame.draw.rect(surface, (200,200,255), (x, y, 120, 40))
                draw_text(surface, str(value), (x+40, y+8))
                x += 140

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

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

    def stack_visualiser(surface):
        stack = []
        input_value = ""
        running = True

        while running:
            surface.fill((230, 230, 255))
            draw_text(surface, "STACK VISUALISER (ESC to return)", (220, 20))

            pygame.draw.rect(surface, (255,255,255), (300, 80, 200, 40))
            draw_text(surface, input_value, (310, 85))

            push_btn = pygame.Rect(250, 140, 120, 40)
            pop_btn  = pygame.Rect(430, 140, 120, 40)

            pygame.draw.rect(surface, (180,180,250), push_btn)
            pygame.draw.rect(surface, (250,180,180), pop_btn)

            draw_text(surface, "PUSH", (push_btn.x+25, push_btn.y+8))
            draw_text(surface, "POP", (pop_btn.x+35, pop_btn.y+8))

            y = HEIGHT - 80

            for value in reversed(stack):
                pygame.draw.rect(surface, (150,200,255), (340, y, 120, 40))
                draw_text(surface, str(value), (380, y+8))
                y -= 50

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

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

    # MAIN MENU FOR THIS MODULE
    bst_btn = pygame.Rect(300, 150, 200, 50)
    ll_btn  = pygame.Rect(300, 230, 200, 50)
    q_btn   = pygame.Rect(300, 310, 200, 50)
    s_btn   = pygame.Rect(300, 390, 200, 50)

    running = True

    while running:
        screen.fill((240, 240, 240))

        draw_text(screen, "DATA STRUCTURE VISUALISER", (220, 50))

        pygame.draw.rect(screen, (200,230,255), bst_btn)
        pygame.draw.rect(screen, (200,255,200), ll_btn)
        pygame.draw.rect(screen, (255,230,200), q_btn)
        pygame.draw.rect(screen, (255,200,230), s_btn)

        draw_text(screen, "BST", (bst_btn.x+75, bst_btn.y+10))
        draw_text(screen, "LINKED LIST", (ll_btn.x+35, ll_btn.y+10))
        draw_text(screen, "QUEUE", (q_btn.x+65, q_btn.y+10))
        draw_text(screen, "STACK", (s_btn.x+65, s_btn.y+10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ESC to return to main menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if bst_btn.collidepoint(event.pos):
                    bst_visualiser(screen)

                if ll_btn.collidepoint(event.pos):
                    linked_list_visualiser(screen)

                if q_btn.collidepoint(event.pos):
                    queue_visualiser(screen)

                if s_btn.collidepoint(event.pos):
                    stack_visualiser(screen)

