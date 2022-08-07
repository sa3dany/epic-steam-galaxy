import json
from os import getenv, path
from pathlib import Path


class GogGame:
    """Returns a new GogGame instance."""

    def __init__(self, info_path):
        self._path = str(info_path.parent)
        self._info = json.load(open(info_path))

        self.type = "GOG"
        self.id = self._info["gameId"]
        self.name = self._info["name"]
        self.primary_task = self._get_primary_task()
        self.is_dlc = self.id != self._info["rootGameId"]

    def _get_primary_task(self):
        tasks = self._info["playTasks"]
        primary_tasks = [t for t in tasks if t.get("isPrimary", False)]
        if len(primary_tasks) > 1:
            pass  # Not possible
        elif len(primary_tasks) == 0:
            return []
        else:
            return primary_tasks[0]

    def get_exe(self):
        """Get the executable path of the game."""

        primaryTask = self._get_primary_task()
        return path.join(self._path, primaryTask["path"])

    def get_launcher_exe(self):
        """Get the GOG Galaxy client exe path"""

        programfiles = getenv("programfiles(x86)")
        return path.join(programfiles, "GOG Galaxy", "GalaxyClient.exe")

    def get_args(self):
        """Get the Arguments (if-any) of the primary play task."""

        primaryTask = self._get_primary_task()
        return primaryTask.get("arguments", "")

    def get_pwd(self):
        """Get the game executable's working directory."""

        primaryTask = self._get_primary_task()
        if primaryTask.get("workingDir", False):
            return path.join(self._path, primaryTask["workingDir"])
        else:
            return self._path

    def get_icon(self):
        """Get the path for the ico file of the game."""

        iconFile = "goggame-" + self.id + ".ico"
        return path.join(self._path, iconFile)

    def get_launcher_args(self):
        """Get the command line arguments to launch the game through GOG
        Galaxy.
        """

        return "/command=runGame" + f' /gameId={self.id} /path="{self.get_pwd()}"'


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