# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from platform import system

from click import command, echo, style

from atos import get_installed_games
from steam import (get_user_ids, get_userdata_path, load_shortcuts,
                   create_shortcut, save_shortcuts)
from util import echo_debug, echo_error, echo_info, truncate_default_shortcut_fields


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def is_windows():
    return system() == "Windows"


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------
@command()
def sync_shortcuts():
    """Sync shortcuts.vdf with installed games"""

    # Get steam's profiles path
    userdata_path = get_userdata_path()
    if not userdata_path:
        echo_error("Could not find Steam's profiles path")
        exit(1)

    # Get the list of users on the system
    ids = get_user_ids(userdata_path)

    # if more than one user, error out for now
    if len(ids) > 1:
        echo_error("Multiple Steam users are not supported yet")
        exit(1)

    user_id = ids[0]
    echo_info(
        f"Syncing shortcuts for Steam user: {style(user_id, fg='green')}")

    echo()

    # load existing shortcuts
    shortcuts = load_shortcuts(user_id)
    echo_info(f"Loaded {len(shortcuts['shortcuts'])} existing shortcut(s)")
    for i, shortcut in shortcuts['shortcuts'].items():
        echo_debug(f"{i}: {truncate_default_shortcut_fields(shortcut)}")

    echo()

    # Get installed games
    games = get_installed_games()
    echo_info(f"Found {len(games)} installed game(s)")

    for game in games:
        echo_info(f" - {style(game.platform, fg='yellow')} {game.name}")

        # create shortcut
        game_shortcut = create_shortcut(game.id,
                                        game.name,
                                        game.exe_path,
                                        icon=game.icon_path,
                                        launch_options=game.args,
                                        tags=[game.platform])

        echo_debug(f"{truncate_default_shortcut_fields(game_shortcut)}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if not is_windows():
        echo_error(f"Unsupported OS: {style(system(), fg='green')}")
        exit(1)

    sync_shortcuts()
