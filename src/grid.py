import numpy as np
import pygame
import random
import typing
from .constants import CELL_SIZE, COLS, ROWS
from .elements import elements, get_element, Element, CommandError

random.seed()

class Grid:
    def __init__(self):
        self.cell_size = CELL_SIZE
        self.grid = np.zeros((ROWS, COLS), dtype=int)
        self.data = {
            "ordered":{
                "value":True
            },
            "extra":{
            }
        }

    def draw(self, screen: pygame.Surface):
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
                    self.data["ordered"] |= {"value":True}
                    need_doing = list(range(len(element.behaviors)))
                    while True:
                        if len(need_doing) == 0:
                                break
                        if self.data["ordered"]["value"]:
                            new = min(need_doing)
                        else:
                            new = random.choice(need_doing)
                        need_doing.remove(new)
                        behavior = element.behaviors[new]
                        actions = self.apply_behavior(row, col, behavior, self.data)
                        for action in actions:
                            if action["action"] == "skip":
                                skipval = action["value"] + new
                                if skipval in need_doing:
                                    need_doing.remove(skipval)
                            else:
                                raise AssertionError(f"Invalid action: {action}")


    def apply_behavior(self,row:int,col:int,behavior:dict[str,str|tuple[int,int]],data:dict[str,dict[str,bool]|dict[int,int]])->list[dict[str,str|int]]:
        output_actions = []
        if behavior["type"] == "action":
            condition = behavior['condition']
            target = behavior['target']
            action = behavior['action'].upper()
            action_coords = behavior['action_coords']
            chance = behavior["chance"]
            skips = behavior["skips"]
            
            target_row = row + condition[1]
            target_col = col + condition[0]
            if 0 <= target_row < ROWS and 0 <= target_col < COLS:
                target_element_id = self.grid[target_row, target_col]
                target_element = get_element(target_element_id)
                
                if target_element.id == target:
                    action_row = row + action_coords[1]
                    action_col = col + action_coords[0]
                    if 0 <= action_row < ROWS and 0 <= action_col < COLS:
                        if random.random() < chance:
                            if action == "SWAP":
                                self.grid[target_row, target_col], self.grid[row, col] = self.grid[row, col], self.grid[target_row, target_col]
                            else:
                                raise CommandError(f"Invalid action: {action}. Please check that it exists and it is spelled correctly.")
                        else:
                            skips = []
                else:
                    skips = []
            for skip in skips:
                output_actions.append({"action":"skip","value":skip})
        elif behavior["type"] == "data":
            change = behavior["change"]
            for key in data:
                try:
                    data[key] |= change[key]
                except KeyError:
                    pass
        else:
            raise AssertionError("Invalid behavior type")
        return output_actions
    
    @staticmethod
    def rectpos(lx:int,ly:int,sx:int=0,sy:int=0)->list[tuple[int,int]]:
        spots = []
        for x in range(lx + 1):
            for y in range(ly + 1):
                spots.append((sx + x, sy + y))
        return spots
    
    def processcells(self, cells: list[tuple[int, int]], placewith: Element) -> None:
        for x, y in cells:
            if x >= 0 and y >= 0:
                if x < ROWS and y < COLS:
                    self.set_cell(x, y, placewith)

    def set_cell(self, row: int, col: int, element: Element):
        element_id = list(elements.values()).index(element)
        self.grid[row, col] = element_id
    
    def set_cells(self, row: int, col: int, element: Element, size: int = 1) -> None:
        csize = size - 1
        hcs = csize / 2
        bsx = row - hcs
        bsy = col - hcs
        bex = row + hcs
        bey = col + hcs
        bdx = bex - bsx
        bdy = bey - bsy
        spots = Grid.rectpos(round(bdx), round(bdy), round(bsx), round(bsy))
        self.processcells(spots, element)