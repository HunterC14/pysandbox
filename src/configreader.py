def readconf() -> dict:
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
    print("Config loaded")
    return config