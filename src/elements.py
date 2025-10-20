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

def parseelement(behavior: str | None):
    if behavior is None:
        return None
    match1 = re.match(r"^\(([-\d]+),([-\d]+)\)$", behavior)
    match2 = re.match(r"(\w+)", behavior)
    match1: re.Match | None
    match2: re.Match | None
    if match1:
        return {
            "type": "element_coords",
            "value": (int(match1.group(1)), int(match1.group(2)))
        }
    if match2:
        return {
            "type": "literal",
            "value": match2.group(1)
        }
def parse_behavior(behavior: str) -> dict[str, tuple[int, int] | tuple[int, str] | str | int]:
    match1 = re.match(r"^IF (.+) (.+) THEN (.*)$", behavior)
    match2 = re.match(r"^IFDATA EXTRA KEY:(\d+) (.+) (\d+) THEN (.*)$", behavior)
    match3 = re.match(r"^DO (.*)", behavior)
    if match1 or match2 or match3:
        m2 = re.match(r"^(\w+)\(([-\d]+),([-\d]+)\)( CHANCE (\d{1,3})%)?( AS (.+))?( SKIP \[((-?\d+,?)*)\])?$",match3.group(1)if match3 else match2.group(4)if match2 else match1.group(3))
        if not m2:
            raise CommandError(f"Invalid behavior: {behavior}")
        m2: re.Match
        out1 = {
            "type":"action",
            "action": m2.group(1),
            "action_coords": (int(m2.group(2)), int(m2.group(3))),
            "chance": (int(m2.group(5))/100) if (m2.group(4) is not None) else 1,
            "skips": _gpuc(m2.group(9)) if m2.group(8) is not None else [],
            "as": parseelement(m2.group(7) if m2.group(6) is not None else None)
        }
        if match1:
            out2 = {
                "cond1": parseelement(match1.group(1)),
                "cond2": parseelement(match1.group(2))
            }
        elif match2:
            out2 = {
                "condition": match2.group(2),
                "target": (int(match2.group(1)),int(match2.group(3))),
                "type":"dataaction"
            }
        elif match3:
            out2 = {
                "type":"doaction"
            }
        else:
            raise AssertionError("Accepted neither correct parse")
        return out1 | out2
    match1 = re.match(r"DATA ORDERED ([01])", behavior)
    if match1:
        return {
            "type":"data",
            "change":{
                "ordered":{"value":bool(int(match1.group(1)))}
            }
        }
    match1 = re.match(r"DATA EXTRA KEY: (\d+) VAL: (\d+)", behavior)
    if match1:
        return {
            "type":"data",
            "change":{
                "extra":{int(match1.group(1)):int(match1.group(2))}
            }
        }
    match1 = re.match(r"DATA EXTRA KEY: (\d+) MOVETO (\d+)", behavior)
    if match1:
        match1: re.Match
        return {
            "type":"data",
            "change":{
                "extra":{int(match1.group(1)):OPERATION('=', int(match1.group(2)))}
            }
        }
    match1 = re.match(r"DATA EXTRA KEY: (\d+) OPERATION (.+) K2 (\d+)", behavior)
    if match1:
        match1: re.Match
        return {
            "type":"data",
            "change": {
                "extra":{int(match1.group(1)):OPERATION(match1.group(2), int(match1.group(3)))}
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
    global keys
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
    keys = list(elements.keys())
    if COMPILER:
        for elem in elements.values():
            elem.compiled = [compiler.compile_code(behavior, keys, elem.id) for behavior in elem.behaviors]

def get_element(element_id: int) -> Element:
    return elements.get(keys[element_id])

def init():
    if COMPILER:
        compiler.load_imports()
    load_elements("elements.txt")
    
