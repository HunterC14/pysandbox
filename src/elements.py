import os
import re

class Element:
    def __init__(self, name: str, eid: str, color: tuple[int, int, int], behaviors: list[dict[str, tuple[int, int] | str]]):
        self.name = name
        self.color = color
        self.behaviors = behaviors
        self.id = eid

class CommandError(Exception): pass

elements = {}

def _gpuc(g: str) -> list[int]:
    ip = re.compile(r"-?\d+")
    im = ip.findall(g)
    return [int(x) for x in im]

def parse_behavior(behavior: str) -> dict[str, tuple[int, int] | str]:
    match = re.match(r"IF \(([-\d]+),([-\d]+)\) (\w+) THEN (\w+)\(([-\d]+),([-\d]+)\) CHANCE (\d{1,3})% SKIP \[((-?\d+,?)*)\]", behavior)
    if match:
        return {
            "type":"action",
            'condition': (int(match.group(1)), int(match.group(2))),
            'target': match.group(3),
            'action': match.group(4),
            'action_coords': (int(match.group(5)), int(match.group(6))),
            "chance": int(match.group(7))/100,
            "skips": _gpuc(match.group(8))
        }
    match = re.match(r"DATA ORDERED ([01])", behavior)
    if match:
        return {
            "type":"data",
            "change":{
                "ordered":{"value":bool(int(match.group(1)))}
            }
        }
    match = re.match(r"DATA EXTRA KEY:(\d+) VAL:(\d+)", behavior)
    if match:
        return {
            "type":"data",
            "change":{
                "extra":{int(match.group(1)):int(match.group(2))}
            }
        }
    raise CommandError(f"Invalid behavior: {behavior}")

def load_elements(filename: str):
    with open(os.path.join(os.path.dirname(__file__),filename), 'r') as file:
        current_element = None
        for line in file:
            line = line.strip()
            if line.startswith("ELEMENT"):
                eid = line.split()[1]
                if current_element:
                    elements[current_element["key"]] = Element(
                        current_element["name"],
                        current_element["key"],
                        current_element["color"],
                        current_element["behaviors"]
                    )
                current_element = {'key': eid, 'behaviors': []}
            elif line.startswith('NAME'):
                current_element['name'] = line.split(maxsplit=1)[1]
            elif line.startswith('COLOR'):
                current_element['color'] = tuple(map(int, line.split()[1].split(',')))
            elif line.startswith('BEHAVIOR'):
                behavior = parse_behavior(line.split(maxsplit=1)[1])
                if behavior:
                    current_element['behaviors'].append(behavior)
            elif line:
                raise CommandError(f"Invalid line: {line}")
        if current_element:
            elements[current_element['key']] = Element(
                current_element['name'],
                eid,
                current_element['color'],
                current_element['behaviors']
            )

def get_element(element_id: int) -> Element:
    keys = list(elements.keys())
    return elements.get(keys[element_id])

load_elements('elements.txt')
