# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from platform import system

from click import command, echo, style

from atos import get_installed_games
from steam import get_profiles_path
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

    # Get steam's profile path
    steam_profiles_path = get_profiles_path()
    if not steam_profiles_path:
        echo_error("Could not find Steam's profiles path")
        exit(1)

    echo_info("Started shortcut sync")

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
