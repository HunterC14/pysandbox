#!/usr/bin/env python3
from src.main import init, main
if __name__ == "__main__":
    screen = init()
    main(screen)
else:
    raise Exception("Not supposed to be imported")