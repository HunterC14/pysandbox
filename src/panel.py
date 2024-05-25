import pygame
from .constants import PANEL_WIDTH, WHITE, BLACK
from .elements import elements, get_element, Element
import typing

class Panel:
    def __init__(self, grid):
        self.width = PANEL_WIDTH
        self.selected_element_id = 1
        self.grid = grid

    def draw(self, screen: pygame.Surface, data: dict[typing.Literal["size"], int]):
        pygame.draw.rect(screen, WHITE, (screen.get_width() - self.width, 0, self.width, screen.get_height()))

        cx = screen.get_width() - self.width + 10
        font = pygame.font.Font(None, 36)
        size_text = font.render(f"Size: {data['size']}", True, BLACK)
        screen.blit(size_text, (cx, 20))
        y = 80
        for element_id, element in elements.items():
            text = font.render(element.name, True, BLACK)
            screen.blit(text, (cx, y))
            if list(elements.keys())[self.selected_element_id] == element_id:
                pygame.draw.rect(screen, element.color, (screen.get_width() - self.width + 5, y - 5, self.width - 10, 30), 2)
            y += 40

    def handle_click(self, x: int, y: int):
        y_offset = 80
        for element_id, element in elements.items():
            if y_offset <= y < y_offset + 30:
                self.selected_element_id = list(elements.keys()).index(element_id)
                break
            y_offset += 40

    @property
    def selected_element(self) -> Element:
        return get_element(self.selected_element_id)
