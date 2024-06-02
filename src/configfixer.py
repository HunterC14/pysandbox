#!/usr/bin/env python3

"""
Config refresher

`configfixer.refresh()` will refresh the config state (remove existing state)
"""

import sys

def refresh():
    print("Config refreshing...")
    if "config" in sys.modules:
        del sys.modules["config"]
        print("Config refreshed!")
    else:
        print("Config already refreshed")