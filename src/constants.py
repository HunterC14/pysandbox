from . import configreader
config = configreader.readconf()
import math

settings = config["settings"]
ws = settings["world"]
display = ws["display"]

ROWS = ws["rows"]
COLS = ws["cols"]
PANEL_WIDTH = display["panel-width"]
CELL_SIZE   = display["cell-size"  ]
WIDTH  = COLS * CELL_SIZE + PANEL_WIDTH
HEIGHT = ROWS * CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def get_kn(keypress: int) -> int:
    key = keypress - 48
    if key > 9 or key < 0:
        raise ValueError(f"Invalid key: (Input: {keypress}, Keyget: {key})")
    return key

def NoneCallable(*params, **kwds):
    if len(params) == 0:
        return
    elif len(params) == 1:
        return params[0]
    return params

def upround(n: int | float) -> int:
    counterpart = n % 1
    if counterpart == .5:
        return math.ceil(n)
    return round(n)

class NamObj:
    def __init__(self, name: str):
        if type(name) is not str:
            raise TypeError("Name must be string.")
        self.name = name
    def __eq__(self, other: "NamObj"):
        return self.name == other.name
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)

class OPERATION:
    def __init__(self, op: str, n: int):
        self.n = n
        self.op = op
    def __str__(self):
        return f"OPERATION {self.op} EK{str(self.n)}"
    def __repr__(self):
        return str(self)

READ = NamObj("READ")