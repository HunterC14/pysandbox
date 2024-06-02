from . import config

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

READ = NamObj("READ")