# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from platform import system

from click import command, echo, style

from atos import get_installed_games
from steam import get_userdata_path, get_user_ids
from util import echo_error, echo_info, echo_debug


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

    # Get installed games
    games = get_installed_games()

    for game in games:
        echo_info(f"{style(game.platform, fg='yellow')} {game.name}")
        echo_debug(
            f"{game.id}, {game.exe_path}, {game.args}, {game.icon_path}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if not is_windows():
        echo_error(f"Unsupported OS: {style(system(), fg='green')}")
        exit(1)

    sync_shortcuts()
