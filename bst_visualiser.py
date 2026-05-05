import pygame
import sys
import math

WIDTH, HEIGHT = 800, 600

def draw_text(surface, text, pos, font, color=(0,0,0)):
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

def draw_tree(screen, node, x, y, dx, font):
    if node is None:
        return

    pygame.draw.circle(screen, (180,200,255), (x, y), 25)
    draw_text(screen, str(node.value), (x-10, y-10), font)

    if node.left:
        pygame.draw.line(screen, (0,0,0), (x, y), (x-dx, y+80), 3)
        draw_tree(screen, node.left, x-dx, y+80, dx//2, font)

    if node.right:
        pygame.draw.line(screen, (0,0,0), (x, y), (x+dx, y+80), 3)
        draw_tree(screen, node.right, x+dx, y+80, dx//2, font)

def bst_visualiser(screen):
    FONT = pygame.font.SysFont(None, 28)

    root = None
    input_value = ""
    traversal_text = ""
    running = True

    while running:
        screen.fill((255, 240, 255))

        draw_text(screen, "BST VISUALISER (ESC to return)", (250, 20), FONT)

        pygame.draw.rect(screen, (255,255,255), (300, 80, 200, 40))
        draw_text(screen, input_value, (310, 85), FONT)

        insert_btn = pygame.Rect(350, 140, 120, 40)
        inorder_btn = pygame.Rect(150, 500, 120, 40)
        preorder_btn = pygame.Rect(330, 500, 120, 40)
        postorder_btn = pygame.Rect(510, 500, 120, 40)

        pygame.draw.rect(screen, (180,250,180), insert_btn)
        pygame.draw.rect(screen, (200,200,255), inorder_btn)
        pygame.draw.rect(screen, (200,200,255), preorder_btn)
        pygame.draw.rect(screen, (200,200,255), postorder_btn)

        draw_text(screen, "INSERT", (insert_btn.x+25, insert_btn.y+8), FONT)
        draw_text(screen, "INORDER", (inorder_btn.x+15, inorder_btn.y+8), FONT)
        draw_text(screen, "PREORDER", (preorder_btn.x+5, preorder_btn.y+8), FONT)
        draw_text(screen, "POSTORDER", (postorder_btn.x+5, postorder_btn.y+8), FONT)

        # Draw tree
        draw_tree(screen, root, WIDTH//2, 200, 200, FONT)

        draw_text(screen, traversal_text, (50, 450), FONT)

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
                    root = insert(root, int(input_value))
                    input_value = ""

                if inorder_btn.collidepoint(event.pos):
                    traversal_text = "Inorder: " + inorder(root)

                if preorder_btn.collidepoint(event.pos):
                    traversal_text = "Preorder: " + preorder(root)

                if postorder_btn.collidepoint(event.pos):
                    traversal_text = "Postorder: " + postorder(root)

def inorder(node):
    if not node: return ""
    return inorder(node.left) + f"{node.value} " + inorder(node.right)

def preorder(node):
    if not node: return ""
    return f"{node.value} " + preorder(node.left) + preorder(node.right)

def postorder(node):
    if not node: return ""
    return postorder(node.left) + postorder(node.right) + f"{node.value} "
