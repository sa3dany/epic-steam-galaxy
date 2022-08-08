# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from platform import system

from click import command, echo, style

from atos import get_installed_games
from util import echo_error


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
    echo("Syncing shortcuts...")
    for game in get_installed_games():
        pass


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if not is_windows():
        echo_error(f"Unsupported OS: {style(system(), fg='green')}")
        exit(1)

    sync_shortcuts()
