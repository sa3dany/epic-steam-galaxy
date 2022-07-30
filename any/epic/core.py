import json
from os import path
from pathlib import Path

MANIFESTS_DIR = "C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"


class EpicGame:
    """Returns a new EpicGame instance"""

    def __init__(self, manifest):
        self._manifest = manifest

        self.id = self._manifest["CatalogItemId"]
        self.name = self._manifest["DisplayName"]

    def get_exe(self):
        """Get executable path of the game"""

        return path.join(
            self._manifest["InstallLocation"], self._manifest["LaunchExecutable"]
        )

    def get_pwd(self):
        return self._manifest["InstallLocation"]

    def get_args(self):
        return ""


def get_installed():
    """Get installed Epic launcher games."""

    games = []
    manifest_files = Path(MANIFESTS_DIR).glob("./*.item")
    for manifest_file in manifest_files:
        manifest = json.load(open(manifest_file))
        game = EpicGame(manifest)
        games.append(game)

    return games
