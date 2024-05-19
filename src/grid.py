import numpy as np
import pygame
from constants import CELL_SIZE, COLS, ROWS
from elements import elements, get_element, Element, CommandError

class Grid:
    def __init__(self):
        self.cell_size = CELL_SIZE
        self.grid = np.zeros((ROWS, COLS), dtype=int)

    def draw(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                element_id = self.grid[row, col]
                element = get_element(element_id)
                pygame.draw.rect(screen, element.color, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))

    def update(self):
        for row in range(ROWS - 2, -1, -1):
            for col in range(COLS):
                element_id = self.grid[row, col]
                element = get_element(element_id)
                if element:
                    for behavior in element.behaviors:
                        self.apply_behavior(row, col, behavior)

    def apply_behavior(self, row: int, col: int, behavior: dict[str, str | tuple[int, int]]):
        condition = behavior['condition']
        target = behavior['target']
        action = behavior['action'].upper()
        action_coords = behavior['action_coords']
        
        target_row = row + condition[1]
        target_col = col + condition[0]
        if 0 <= target_row < ROWS and 0 <= target_col < COLS:
            target_element_id = self.grid[target_row, target_col]
            target_element = get_element(target_element_id)
            
            if target_element.id == target:
                action_row = row + action_coords[1]
                action_col = col + action_coords[0]
                if 0 <= action_row < ROWS and 0 <= action_col < COLS:
                    if action == "SWAP":
                        self.grid[target_row, target_col], self.grid[row, col] = self.grid[row, col], self.grid[target_row, target_col]
                    else:
                        raise CommandError(f"Invalid action: {action}. Please check that it exists and it is spelled correctly.")

    def set_cell(self, row: int, col: int, element: Element):
        element_id = list(elements.values()).index(element)
        self.grid[row, col] = element_id
