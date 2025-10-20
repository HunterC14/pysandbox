"""
COMPILER
"""
import random
from .constants import ROWS, COLS, OPERATION, CommandError, config
from copy import copy
def load_imports():
    global get_element
    from .elements import get_element
from typing import Callable

def compile_code(behavior:dict[str,str|tuple[int,int]], keys: list, element_id)->Callable:
    code = ""
    if behavior["type"] in ("action","dataaction","doaction"):
        action = behavior["action"].upper()
        action_coords = behavior["action_coords"]
        chance = behavior["chance"]
        skips = behavior["skips"]
        aselm = behavior["as"]
        if aselm is not None and aselm["type"] == "literal" and aselm["value"] not in keys:
            raise CommandError("No such element "+aselm)
        code += f"skips = {skips}\n"
        code += """
data = {}
data["extra"] = self.datagrid[row][col]
data["ordered"] = {"value":True}
accept = True
"""
        match behavior["type"]:
            case "action":
                code += "accept = True\n"
                cond1 = behavior["cond1"]
                cond2 = behavior["cond2"]
                cond1v = cond1["value"]
                cond2v = cond2["value"]
                if cond1["type"] == "element_coords":
                    code += f"""
target_1_row = row + {cond1v[1]}
target_1_col = col + {cond1v[0]}
if 0 <= target_1_row < {ROWS} and 0 <= target_1_col < {COLS}:
    target_1_element_id = self.grid[target_1_row, target_1_col]
    target_1_element = get_element(target_1_element_id).id
else:
    accept = False
    skips = []
"""
                elif cond1["type"] == "literal":
                    code += f"""
target_1_element = "{cond1v}"
"""
                if cond2["type"] == "element_coords":
                    code += f"""
target_2_row = row + {cond2v[1]}
target_2_col = col + {cond2v[0]}
if 0 <= target_2_row < {ROWS} and 0 <= target_2_col < {COLS}:
    target_2_element_id = self.grid[target_2_row, target_2_col]
    target_2_element = get_element(target_2_element_id).id
else:
    accept = False
    skips = []
"""
                elif cond2["type"] == "literal":
                    code += f"""
target_2_element = "{cond2v}"
"""
                code += """
if accept:
    accept = target_1_element == target_2_element\n
"""
                
            case "dataaction":
                condition = behavior["condition"]
                target = behavior["target"]
                code += f"""
n = data["extra"][{target[0]}]
n2 = data["extra"][{target[1]}]
accept = """+{"=":"n==n2",">":"n>n2","<":"n<n2",">=":"n>=n2","<=":"n<=n2"}[condition]+"\n"

            case "doaction":
                code += "accept = True\n"
            case err:
                raise AssertionError(f"not action or dataaction: {err}")
        if chance < 1:
            code += f"""
if random.random() > {chance}:
    accept = False"""
        code += f"""
if accept:
    action_row = row + {action_coords[1]}
    action_col = col + {action_coords[0]}
    if 0 <= action_row < {ROWS} and 0 <= action_col < {COLS}:
"""
        if aselm is None:
            code += f"""
        ne = {keys.index(element_id)}
"""
        elif aselm["type"] == "literal":
            code += f"""
        ne = {keys.index(aselm["value"])}
"""
        elif aselm["type"] == "element_coords":
            code += f"""
        ne = self.grid[row + {aselm["value"][1]},col + {aselm["value"][0]}]
"""
        if action == "SWAP":
            code += """
        self.grid[action_row, action_col], self.grid[row, col] = ne, self.grid[action_row, action_col]
        if ne == self.grid[row, col]:
            self.datagrid[action_row][action_col], self.datagrid[row][col] = copy(self.datagrid[row][col]), deepcopy(self.datagrid[action_row][action_col])
        else:
            self.datagrid[row][col] = copy(self.datagrid[action_row][action_col])
        output_actions.append({"action":"move","value":(action_row, action_col)})\n"""
        elif action == "COPY":
            code += """
        self.grid[action_row, action_col] = ne
        if ne == self.grid[row, col]:
            self.datagrid[action_row][action_col] = copy(self.datagrid[row][col])\n"""
        else:
            raise CommandError(f"Invalid action: {action}.")
        code += """
    else:
        skips = []
else:
    skips = []
for skip in skips:
    output_actions.append({"action":"skip","value":skip})
"""
    elif behavior["type"] == "data":
        change: dict[str, dict[str | int, int | OPERATION]] = behavior["change"]
        if "ordered" in change:
            code += f"data[\"ordered\"] |= {change['ordered']}\n"
        if "extra" in change:
            if change["extra"] is None:
                code += "self.datagrid[row][col] = {}\n"
            else:
                for key in change["extra"].keys():
                    val = change["extra"][key]
                    if type(val) is int:
                        code += f"data[\"extra\"][{key}] = {val}\n"
                    elif type(val) is OPERATION:
                        code += f"ex = data[\"extra\"]\nex[{repr(key)}] "
                        try:
                            code += {'=':'=','+':'+=','-':'-=','x':'*=','/':'/=','%':'%=','^':'**='}[val.op]
                        except KeyError:
                            raise CommandError("Invalid operation: "+val.op)
                        code += f" ex[{val.n}]\n"
    else:
        raise AssertionError("Invalid behavior type")
    code += """
self.localdata = data"""
    if "debug" in config["settings"] and "pycode-output" in config["settings"]["debug"]:
        with open(config["settings"]["debug"]["pycode-output"], "at") as f:
            f.write(f"\n\n##SPLIT##  {element_id}\n\n"+code)
    compiled = compile(code, "compiled_code","exec")
    def func(self, row, col, data):
        outa = []
        exec(compiled, {"self":self,"row":row,"col":col,"data":data,"output_actions":outa,
        "random":random,"copy":copy,"get_element":get_element})
        return outa
    return func