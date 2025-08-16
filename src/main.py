import pygame
from .grid import Grid
from .panel import Panel
from .constants import WIDTH, HEIGHT, PANEL_WIDTH, get_kn, config
from . import line
from . import configreader

# fix the circular import
from . import elements
elements.init()
del elements

FPS = config["settings"]["runtime"]["FPS"]

def init():
    # Initialize Pygame
    pygame.init()

    # Create the screen
    icon = pygame.image.load("../assets/favicon.png") 
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sand Box")
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
            x, y = pygame.mouse.get_pos()
            if x < WIDTH - PANEL_WIDTH:
                col = x // grid.cell_size
                row = y // grid.cell_size
                if prev_pos is None:
                    grid.set_cells(row, col, panel.selected_element, data["size"])
                else:
                    line.funcline((row,col),prev_pos,grid.set_cells,[panel.selected_element, data["size"]])
            prev_pos = (row,col)

        grid.draw(screen)
        panel.draw(screen, data)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    screen = init()
    main(screen)
