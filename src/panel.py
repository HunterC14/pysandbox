import pygame
from .constants import PANEL_WIDTH, WHITE, BLACK
from .elements import elements, get_element, Element

class Panel:
    def __init__(self, grid):
        self.width = PANEL_WIDTH
        self.selected_element_id = 1  # Default to 'Sand'
        self.grid = grid

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, WHITE, (screen.get_width() - self.width, 0, self.width, screen.get_height()))

        font = pygame.font.Font(None, 36)
        y = 20
        for element_id, element in elements.items():
            text = font.render(element.name, True, BLACK)
            screen.blit(text, (screen.get_width() - self.width + 10, y))
            if list(elements.keys())[self.selected_element_id] == element_id:
                pygame.draw.rect(screen, element.color, (screen.get_width() - self.width + 5, y - 5, self.width - 10, 30), 2)
            y += 40

    def handle_click(self, x: int, y: int):
        y_offset = 20
        for element_id, element in elements.items():
            if y_offset <= y < y_offset + 30:
                self.selected_element_id = list(elements.keys()).index(element_id)
                break
            y_offset += 40

    @property
    def selected_element(self) -> Element:
        return get_element(self.selected_element_id)
