from any.epic import get_installed as get_epic_installed
from any.gog import get_gog_games
from steam import load_shortcuts, make_shortcut, save_shortcuts
from util import unquote_string

shortcuts = load_shortcuts("280467180")
print(f"Parsed existing shortcuts.vdf")

# Launcher Games
gog_games = get_gog_games("C:\Program Files (x86)\GOG Galaxy\Games")
print(f"Found {len(gog_games)} [GOG] installed games")

epic_games = get_epic_installed()
print(f"Found {len(epic_games)} [Epic] installed games")

games = []
games.extend(gog_games)
games.extend(epic_games)

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
        if (
            unquote_string(shortcut["Exe"]) == game.get_exe()
            or shortcut["AppName"] == game.name
            or shortcut["DevkitGameID"] == game.id
        ):
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

# Save updated shortcuts
save_shortcuts("280467180", {"shortcuts": new_shortcuts})
print("Saved new shortcuts.vdf")
