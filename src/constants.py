WIDTH = 900
HEIGHT = 600
PANEL_WIDTH = 100
CELL_SIZE = 5
ROWS = HEIGHT // CELL_SIZE
COLS = (WIDTH - PANEL_WIDTH) // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def get_kn(keypress: int) -> int:
    key = keypress - 48
    if key > 9 or key < 0:
        raise ValueError(f"Invalid key: (Input: {keypress}, Keyget: {key})")
    return key