import numpy as np
import pygame
import random
from copy import copy
#from typing import Literal
from .constants import CELL_SIZE, COLS, ROWS, READ, NamObj, NoneCallable, upround, OPERATION, COMPILER, CommandError, config
import typing
from .elements import elements, get_element, Element

def init():
    global keys
    from .elements import keys

cell_count = ROWS * COLS
random.seed()

class Grid:
    def __init__(self, conf: dict | NamObj = READ):
        self.cell_size = CELL_SIZE
        self.grid = np.zeros((ROWS, COLS), dtype=int)
        self.datagrid = [[{} for _ in range(COLS)] for _ in range(ROWS)]
        if conf is READ:
            conf = config
        active_settings = conf["settings"]
        update_settings = active_settings["update"]
        self.order = update_settings["activation-order"]
        self.quantity = update_settings["quantity"]

    def draw(self, screen: pygame.Surface):
        for row in range(ROWS):
            for col in range(COLS):
                element_id = self.grid[row, col]
                element = get_element(element_id)
                pygame.draw.rect(screen, element.color, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))

    def processcell(self, row: int, col: int):
        element_id = self.grid[row, col]
        element = get_element(element_id)
        if element:
            self.localdata = {"ordered":{"value":1},"extra":{}}
            need_doing = list(range(len(element.behaviors)))
            while True:
                if len(need_doing) == 0:
                        break
                if self.localdata["ordered"]["value"]:
                    new = min(need_doing)
                else:
                    new = random.choice(need_doing)
                need_doing.remove(new)
                if COMPILER:
                    actions = element.compiled[new](self,row,col,self.localdata)
                else:
                    raise NotImplementedError("Interpreter no longer supported.")
                for action in actions:
                    if action["action"] == "skip":
                        skipval = action["value"] + new
                        if skipval in need_doing:
                            need_doing.remove(skipval)
                    elif action["action"] == "move":
                        row, col = action["value"]
                    else:
                        raise AssertionError(f"Invalid action: {action}")

    def update(self):
        def process1to4(cd:int,R:int,S1:int,X1:int,C:int,S2:int,X2:int)->None:
            for row in range(R, S1, X1):
                for col in range(C, S2, X2):
                    if cd == 0:
                        return
                    self.processcell(row, col)
                    cd -= 1
        order = self.order
        quantity = self.quantity
        countdown = round(quantity * cell_count)
        if order == 0:
            undone = list(range(cell_count))
            random.shuffle(undone)
            for n in undone:
                if countdown == 0:
                    break
                row, col = divmod(n, COLS)
                self.processcell(row, col)
                countdown -= 1
        elif order == 1:
            process1to4(countdown, ROWS - 1, -1, -1, 0, COLS, 1)
        elif order == 2:
            process1to4(countdown, 0, ROWS, 1, 0, COLS, 1)
        elif order == 3:
            process1to4(countdown, 0, ROWS, 1, COLS - 1, -1, -1)
        elif order == 4:
            process1to4(countdown, ROWS - 1, -1, -1, COLS - 1, -1, -1)
        else:
            assert False, f"Invalid order, {order}"


    def _old_interpreter(self,row:int,col:int,behavior:dict[str,str|tuple[int,int]],data:dict[str,dict[str,bool]|dict[int,int]])->list[dict[str,str|int]]:
        output_actions = []
        if behavior["type"] in ("action","dataaction","doaction"):
            if behavior["type"] != "doaction":
                condition = behavior['condition']
                target = behavior['target']
            action = behavior['action'].upper()
            action_coords = behavior['action_coords']
            chance = behavior["chance"]
            skips = behavior["skips"]
            aselm = behavior["as"]
            data["extra"] = self.datagrid[row][col]
            
            accept = False
            match behavior["type"]:
                case "action":
                    target_row = row + condition[1]
                    target_col = col + condition[0]
                    if 0 <= target_row < ROWS and 0 <= target_col < COLS:
                        target_element_id = self.grid[target_row, target_col]
                        target_element = get_element(target_element_id)
                        accept = target_element.id == target
                    else:
                        skips = []
                case "dataaction":
                    n = data["extra"][condition[0]]
                    n2 = data["extra"][target]
                    accept = {"=":n==n2,">":n>n2,"<":n<n2,">=":n>=n2,"<=":n<=n2}[condition[1]]
                case "doaction":
                    accept = True
                case err:
                    raise AssertionError(f"not action or dataaction: {err}")

            if accept:
                action_row = row + action_coords[1]
                action_col = col + action_coords[0]
                if 0 <= action_row < ROWS and 0 <= action_col < COLS:
                    if random.random() < chance:
                        if aselm is None:
                            ne = self.grid[row][col]
                        else:
                            ne = keys.index(aselm)
                        if action == "SWAP":
                            self.grid[action_row, action_col], self.grid[row, col] = ne, self.grid[action_row, action_col]
                            if ne == self.grid[row, col]:
                                self.datagrid[action_row][action_col], self.datagrid[row][col] = copy(self.datagrid[row][col]), copy(self.datagrid[action_row][action_col])
                            else:
                                self.datagrid[row][col] = copy(self.datagrid[action_row][action_col])
                            output_actions.append({"action":"move","value":(action_row, action_col)})
                        elif action == "COPY":
                            self.grid[action_row, action_col] = ne
                            if ne == self.grid[row, col]:
                                self.datagrid[action_row][action_col] = copy(self.datagrid[row][col])
                        else:
                            raise CommandError(f"Invalid action: {action}.")
                    else:
                        skips = []
                else:
                    skips = []
            else:
                skips = []
            for skip in skips:
                output_actions.append({"action":"skip","value":skip})
        elif behavior["type"] == "data":
            change: dict[str, dict[str | int, int | OPERATION]] = behavior["change"]
            if "ordered" in change:
                data["ordered"] |= change["ordered"]
            if "extra" in change:
                if change["extra"] is None:
                    data["extra"] = {}
                    self.datagrid[row][col] = {}
                else:
                    for key in change["extra"].keys():
                        val = change["extra"][key]
                        if type(val) is int:
                            data["extra"][key] = val
                        elif type(val) is OPERATION:
                            ex = data["extra"]
                            v = ex[val.n]
                            match val.op:
                                case '=':
                                    ex[key] = v
                                case '+':
                                    ex[key] += v
                                case '-':
                                    ex[key] -= v
                                case 'x':
                                    ex[key] *= v
                                case '/':
                                    ex[key] /= v
                                case '%':
                                    ex[key] %= v
                                case '^':
                                    ex[key] **= v
                                case e:
                                    raise CommandError(f"Invalid operation type: {e}")
        else:
            raise AssertionError("Invalid behavior type")
        self.datagrid[row][col] |= data["extra"]
        self.localdata = data
        return output_actions
    
    @staticmethod
    def rectpos(lx:int|float,ly:int|float,sx:int|float=0,sy:int|float=0,apply:typing.Callable[[int|float],int|float]=NoneCallable)->list[tuple[int,int]]:
        spots = []
        dpartx = lx % 1
        dparty = ly % 1
        flx = round(lx - dpartx)
        fly = round(ly - dparty)
        for x in range(flx + 1):
            for y in range(fly + 1):
                spots.append((apply(sx + x + dpartx), apply(sy + y + dparty)))
        return spots
    
    def processcells(self, cells: list[tuple[int, int]], placewith: Element) -> None:
        for x, y in cells:
            if x >= 0 and y >= 0:
                if x < ROWS and y < COLS:
                    self.set_cell(x, y, placewith)

    def set_cell(self, row: int, col: int, element: Element):
        element_id = list(elements.values()).index(element)
        self.grid[row, col] = element_id
        self.datagrid[row][col] = copy(element.datadef)
    
    def set_cells(self, row: int, col: int, element: Element, size: int = 1) -> None:
        csize = size - 1
        hcs = csize / 2
        bsx = row - hcs
        bsy = col - hcs
        bex = row + hcs
        bey = col + hcs
        bdx = bex - bsx
        bdy = bey - bsy
        spots = Grid.rectpos(bdx, bdy, bsx, bsy, upround)
        self.processcells(spots, element)