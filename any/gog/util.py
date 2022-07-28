from os import getenv, path
from pathlib import Path


from any.gog.game import GogGame


def get_gog_games(path):
    """Get GOG games."""

    games = []
    info_files = Path(path).glob("./*/goggame-*.info")
    for info_file in info_files:
        game = GogGame(info_file)
        if not game.is_dlc:
            games.append(game)
    return games


def get_galaxy_path():
    """Get the GOG Galaxy client install path"""

    programfiles = getenv("programfiles(x86)")
    return path.join(programfiles, "GOG Galaxy")


def get_galaxy_exe():
    """Get the GOG Galaxy client exe path"""

    programfiles = getenv("programfiles(x86)")
    return path.join(programfiles, "GOG Galaxy", "GalaxyClient.exe")
