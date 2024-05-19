import pygame
from .grid import Grid
from .panel import Panel
from .constants import WIDTH, HEIGHT, PANEL_WIDTH, BLACK

def init():
    # Initialize Pygame
    pygame.init()

    # Create the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Falling Sand Game')
    return screen

def main(screen):
    clock = pygame.time.Clock()
    running = True
    mouse_down = False

    grid = Grid()
    panel = Panel(grid)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x > WIDTH - PANEL_WIDTH:
                    panel.handle_click(x, y)
                else:
                    mouse_down = True

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False

        if mouse_down:
            x, y = pygame.mouse.get_pos()
            if x < WIDTH - PANEL_WIDTH:
                col = x // grid.cell_size
                row = y // grid.cell_size
                grid.set_cell(row, col, panel.selected_element)

        grid.update()

        screen.fill(BLACK)
        grid.draw(screen)
        panel.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    screen = init()
    main(screen)
