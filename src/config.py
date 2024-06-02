# THIS IS A MODULE (module but not, overwrites to be the return value)
def mainload():
    global config
    import os
    import json
    os.chdir(os.path.dirname(__file__))
    # attempt load config
    print("Config loading...")
    try:
        with open("config.json","r") as f:
            config = json.load(f)
    except FileNotFoundError:
        # recreate config
        print("Config not found...creating...")
        try:
            with open(".default_config.json","r") as f:
                confstr = f.read()
        except FileNotFoundError:
            # if failed to fix config
            raise SystemExit("Sorry! Not found: '.default_config.json', could not recreate config file!") from None
        with open("config.json","w") as f:
            f.write(confstr)
        config = json.loads(confstr)
        del confstr # indicate temporary
    print("Config loaded")
mainload()
if __name__ == "__main__":
    print(config)
    raise SystemExit
# overwrite import so, "import config" will return the config instead of the module
import sys
sys.modules[__name__] = config
del sys # indicate end of use