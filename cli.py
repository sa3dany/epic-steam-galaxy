from steam import load_shortcuts, make_shortcut, save_shortcuts
from util import unquote_string

shortcuts = load_shortcuts("280467180")

new_shortcuts = {}
for i, game in enumerate(games):
    new_shortcut = make_shortcut(
        id=game.id,
        exe=game.get_launcher_exe(),
        args=game.get_launcher_args(),
        pwd=game.get_pwd(),
        name=game.name,
        icon=game.get_exe(),
        tag=game.type,
    )
    new_shortcuts[str(i)] = new_shortcut

    for shortcut in shortcuts["shortcuts"].values():
        if (unquote_string(shortcut["Exe"]) == game.get_exe()
                or shortcut["AppName"] == game.name
                or shortcut["DevkitGameID"] == game.id):
            if shortcut.get("LastPlayTime", 0) > 0:
                new_shortcut["LastPlayTime"] = shortcut["LastPlayTime"]
                print(f'  ☑ Restored LastPlayTime: {shortcut["AppName"]}')

# Custom (user-created) shortcuts
# Keep them at the end, don't modify them
for shortcut in shortcuts["shortcuts"].values():
    if "GOG" in shortcut["tags"].values():
        continue
    if "EPIC" in shortcut["tags"].values():
        continue
    new_shortcuts[str(len(new_shortcuts))] = shortcut
    print("  ☐ Non-GOG: " + f'{shortcut["AppName"]}')

save_shortcuts("280467180", {"shortcuts": new_shortcuts})
print("Saved new shortcuts.vdf")
