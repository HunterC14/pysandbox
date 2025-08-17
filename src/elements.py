import os
import re
from .constants import OPERATION, COMPILER, CommandError
if COMPILER:
    from . import compiler
    print("using compiler")

class Element:
    def __init__(self, name: str, eid: str, color: tuple[int, int, int], behaviors: list[dict[str, tuple[int, int] | str]], datadef: dict[int, int], compiled: list | None = None):
        self.name = name
        self.color = color
        self.behaviors = behaviors
        self.id = eid
        self.datadef = datadef
        self.compiled = compiled



elements: dict[str,Element] = {}

def _gpuc(g: str) -> list[int]:
    ip = re.compile(r"-?\d+")
    im = ip.findall(g)
    return [int(x) for x in im]

def parse_behavior(behavior: str) -> dict[str, tuple[int, int] | tuple[int, str] | str | int]:
    match = re.match(r"IF \(([-\d]+),([-\d]+)\) (\w+) THEN (.*)", behavior)
    match2 = re.match(r"IFDATA EXTRA KEY:(\d+) (.+) (\d+) THEN (.*)", behavior)
    match3 = re.match(r"DO (.*)", behavior)
    if match or match2 or match3:
        m2 = re.match(r"(\w+)\(([-\d]+),([-\d]+)\) CHANCE (\d{1,3})% AS (\w+) SKIP \[((-?\d+,?)*)\]",match3.group(1)if match3 else match2.group(4)if match2 else match.group(4))
        if not m2:
            raise CommandError(f"Invalid behavior: {behavior}")
        m2: re.Match
        out1 = {
            "type":"action",
            "action": m2.group(1),
            "action_coords": (int(m2.group(2)), int(m2.group(3))),
            "chance": int(m2.group(4))/100,
            "skips": _gpuc(m2.group(6)),
            "as": m2.group(5)
        }
        if match:
            out2 = {
                "condition": (int(match.group(1)), int(match.group(2))),
                "target": match.group(3)
            }
        elif match2:
            out2 = {
                "condition": (int(match2.group(1)), match2.group(2)),
                "target":  int(match2.group(3)),
                "type":"dataaction"
            }
        elif match3:
            out2 = {
                "type":"doaction"
            }
        else:
            raise AssertionError("Accepted neither correct parse")
        return out1 | out2
    match = re.match(r"DATA ORDERED ([01])", behavior)
    if match:
        return {
            "type":"data",
            "change":{
                "ordered":{"value":bool(int(match.group(1)))}
            }
        }
    match = re.match(r"DATA EXTRA KEY: (\d+) VAL: (\d+)", behavior)
    if match:
        return {
            "type":"data",
            "change":{
                "extra":{int(match.group(1)):int(match.group(2))}
            }
        }
    match = re.match(r"DATA EXTRA KEY: (\d+) MOVETO (\d+)", behavior)
    if match:
        match: re.Match
        return {
            "type":"data",
            "change":{
                "extra":{int(match.group(1)):OPERATION('=', int(match.group(2)))}
            }
        }
    match = re.match(r"DATA EXTRA KEY: (\d+) OPERATION (.+) K2 (\d+)", behavior)
    if match:
        match: re.Match
        return {
            "type":"data",
            "change": {
                "extra":{int(match.group(1)):OPERATION(match.group(2), int(match.group(3)))}
            }
        }
    if behavior == "DATA DEL":
        return {
            "type":"data",
            "change": {
                "extra": None
            }
        }

    raise CommandError(f"Invalid behavior: {behavior}")

def load_elements(filename: str):
    with open(os.path.join(os.path.dirname(__file__),filename), 'r') as file:
        current_element = None
        for line in file:
            line = line.strip()
            if line[0] == "#":
                continue # comment
            if line.startswith("ELEMENT"):
                eid = line.split()[1]
                if current_element:
                    elements[current_element["key"]] = Element(
                        current_element["name"],
                        current_element["key"],
                        current_element["color"],
                        current_element["behaviors"],
                        current_element["datadef"],
                    )
                current_element = {"key": eid, "behaviors": [], "datadef": {}}
            elif line.startswith("NAME"):
                current_element["name"] = line.split(maxsplit=1)[1]
            elif line.startswith("COLOR"):
                current_element["color"] = tuple(map(int, line.split()[1].split(",")))
            elif line.startswith("BEHAVIOR"):
                behavior = parse_behavior(line.split(maxsplit=1)[1])
                if behavior:
                    current_element["behaviors"].append(behavior)
            elif line.startswith("DATADEF"):
                current_element["datadef"][int(line.split(' ')[1])] = int(line.split(' ')[2])
            elif line:
                raise CommandError(f"Invalid line: {line}")
        if current_element:
            elements[current_element["key"]] = Element(
                current_element["name"],
                eid,
                current_element["color"],
                current_element["behaviors"],
                current_element["datadef"],
            )
    if COMPILER:
        for elem in elements.values():
            elem.compiled = [compiler.compile_code(behavior, elements) for behavior in elem.behaviors]

def get_element(element_id: int) -> Element:
    keys = list(elements.keys())
    return elements.get(keys[element_id])

def init():
    if COMPILER:
        compiler.load_imports()
    load_elements("elements.txt")
