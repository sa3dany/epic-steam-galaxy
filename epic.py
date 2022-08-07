import json
from os import path
from pathlib import Path
from urllib.parse import quote, urlencode

MANIFESTS_DIR = "C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"


class EpicGame:
    """Returns a new EpicGame instance"""

    def __init__(self, manifest):
        self._manifest = manifest

        self.type = "EPIC"
        self.id = self._manifest["CatalogItemId"]
        self.name = self._manifest["DisplayName"]

    def get_exe(self):
        """Get executable path of the game"""

        return path.join(
            self._manifest["InstallLocation"], self._manifest["LaunchExecutable"]
        )

    def get_launcher_exe(self):
        """Get the Epic launcher exe path (not really!)

        I am doing it the way the add desktop works by using the
        com.epicgames.launcher:// protocol."""

        protocol = "com.epicgames.launcher://"
        base_path = "apps"
        namespace = self._manifest["CatalogNamespace"]
        id = self._manifest["CatalogItemId"]
        name = self._manifest["AppName"]
        query = urlencode({"action": "launch", "silent": "true"})

        path = quote(f"{base_path}/{namespace}:{id}:{name}")
        return f"{protocol}{path}?{query}"

    def get_pwd(self):
        return path.dirname(self.get_exe())

    def get_args(self):
        return ""

    def get_launcher_args(self):
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
