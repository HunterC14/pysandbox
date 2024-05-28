import pygame
from .grid import Grid
from .panel import Panel
from .constants import WIDTH, HEIGHT, PANEL_WIDTH, get_kn
from . import line

def init():
    # Initialize Pygame
    pygame.init()

    # Create the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Falling Sand Game')
    return screen

def main(screen: pygame.Surface):
    clock = pygame.time.Clock()
    running = True
    mouse_down = False
    data = {"size": 1, "paused": 0}

    grid = Grid()
    panel = Panel(grid)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x > WIDTH - PANEL_WIDTH:
                    panel.handle_click(x, y, data)
                else:
                    mouse_down = True
                    prev_pos = None

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
            elif event.type == pygame.KEYUP:
                try:
                    key = get_kn(event.key)
                except ValueError:
                    key = None
                if key is not None:
                    data["size"] = key
        
        if not data["paused"]:
            grid.update()

        if mouse_down:
            x, y = pygame.mouse.get_