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

def parse_behavior(behavior: str) -> None | dict[str, tuple[int, int] | str]:
    match = re.match(r"IF \(([-\d]+),([-\d]+)\) (\w+) THEN (\w+)\(([-\d]+),([-\d]+)\)", behavior)
    if match:
        return {
            'condition': (int(match.group(1)), int(match.group(2))),
            'target': match.group(3),
            'action': match.group(4),
            'action_coords': (int(match.group(5)), int(match.group(6)))
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
