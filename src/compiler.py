"""
COMPILER
"""
import random
from .constants import ROWS, COLS, OPERATION, CommandError
from copy import deepcopy
def load_imports():
    global get_element
    from .elements import get_element
from types import FunctionType

def compile_code(behavior:dict[str,str|tuple[int,int]],elements)->FunctionType:
    code = ""
    if behavior["type"] in ("action","dataaction","doaction"):
        if behavior["type"] != "doaction":
            condition = behavior['condition']
            target = behavior['target']
        action = behavior['action'].upper()
        action_coords = behavior['action_coords']
        chance = behavior["chance"]
        skips = behavior["skips"]
        aselm = behavior["as"]
        code += f"skips = {skips}\n"
        code += """
data = {}
data["extra"] = self.datagrid[row][col]
data["ordered"] = {"value":True}
accept = False
"""
        match behavior["type"]:
            case "action":
                code += f"""
target_row = row + {condition[1]}
target_col = col + {condition[0]}
if 0 <= target_row < {ROWS} and 0 <= target_col < {COLS}:
    target_element_id = self.grid[target_row, target_col]
    target_element = get_element(target_element_id)
    accept = target_element.id == "{target}"
else:
    skips = []
"""
                
            case "dataaction":
                code += f"""
n = data["extra"][{condition[0]}]
n2 = data["extra"][{target}]
accept = """+{"=":"n==n2",">":"n>n2","<":"n<n2",">=":"n>=n2","<=":"n<=n2"}[condition[1]]+"\n"

            case "doaction":
                code += "accept = True\n"
            case err:
                raise AssertionError(f"not action or dataaction: {err}")
        code += f"""
if accept:
    action_row = row + {action_coords[1]}
    action_col = col + {action_coords[0]}
    if 0 <= action_row < {ROWS} and 0 <= action_col < {COLS}:
        if random.random() < {chance}:
            ne = {list(elements.keys()).index(aselm)}
"""
        if action == "SWAP":
            code += """
            self.grid[action_row, action_col], self.grid[row, col] = ne, self.grid[action_row, action_col]
            if ne == self.grid[row, col]:
                self.datagrid[action_row][action_col], self.datagrid[row][col] = deepcopy(self.datagrid[row][col]), deepcopy(self.datagrid[action_row][action_col])
            else:
                self.datagrid[row][col] = deepcopy(self.datagrid[action_row][action_col])
            output_actions.append({"action":"move","value":(action_row, action_col)})\n"""
        elif action == "COPY":
            code += """
            self.grid[action_row, action_col] = ne
            if ne == self.grid[row, col]:
                self.datagrid[action_row][action_col] = deepcopy(self.datagrid[row][col])\n"""
        else:
            raise CommandError(f"Invalid action: {action}.")
        code += """
        else:
            skips = []
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
                        code += str(val.n)+"\n"
    else:
        raise AssertionError("Invalid behavior type")
    code += """
self.datagrid[row][col] |= data["extra"]
self.localdata = data"""
    #print("Compiled code:\n"+code)
    compiled = compile(code, "compiled_code","exec")
    def func(self, row, col, data):
        outa = []
        exec(compiled, {"self":self,"row":row,"col":col,"data":data,"output_actions":outa,
        "random":random,"deepcopy":deepcopy,"get_element":get_element,"elements":elements})
        return outa
    return func