# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from json import load as json_parse
from os.path import expandvars
from pathlib import Path
from urllib.parse import quote, urlencode


# ----------------------------------------------------------------------
# Installed game interface
# ----------------------------------------------------------------------
class Game:
    """Game class."""

    def __init__(
        self,
        platform=None,
        id=None,
        name=None,
        exe_path=None,
        args="",
        icon_path="",
    ):
        if platform is None:
            raise ValueError("Platform is required.")
        if platform not in ["epic", "gog"]:
            raise ValueError(f"Invalid platform: {platform}")
        self.platform = platform

        if id is None:
            raise ValueError("ID is required.")
        self.id = id

        if not name:
            raise ValueError("Name is required.")
        self.name = name

        if not exe_path:
            raise ValueError("Executable path is required.")
        self.exe_path = exe_path

        self.args = args
        self.icon_path = icon_path


# ----------------------------------------------------------------------
# GOG Galaxy
# ----------------------------------------------------------------------
def _get_installed_gog_games():
    """Get installed GOG games."""

    # GOG Galaxy launcher path
    GALAXY_PATH = "%ProgramFiles(x86)%\\GOG Galaxy\\GalaxyClient.exe"

    # Get the game library path
    GALAXY_CONFIG_PATH = "%ProgramData%\\GOG.com\\Galaxy\\config.json"
    config = json_parse(open(expandvars(GALAXY_CONFIG_PATH)))
    library_path = Path(config["libraryPath"])

    # Get the list of installed games info files
    info_files = library_path.glob(".\\*\\goggame-*.info")

    games = []
    for info_file in info_files:
        info = json_parse(open(info_file))

        # Get the game's pwd & icon path
        pwd = str(info_file.parent)
        for task in info["playTasks"]:
            if task.get("isPrimary", False):
                # Use the actual game exe for the icon path
                icon_path = info_file.parent / task["path"]

                # if primary task has a pwd use it instead
                if task.get("workingDir", False):
                    pwd = str(info_file.parent / task["workingDir"])
                    break

        args = f'/command=runGame /gameId={info["gameId"]} /path="{pwd}"'

        # Ignore DLCs
        if info["gameId"] != info["rootGameId"]:
            continue

        game = Game(
            platform="gog",
            id=info["gameId"],
            name=info["name"],
            exe_path=expandvars(GALAXY_PATH),
            args=args,
            icon_path=icon_path,
        )

        games.append(game)

    return games


# ----------------------------------------------------------------------
# Epic Games
# ----------------------------------------------------------------------
def _get_installed_epic_games():
    """Get installed Epic games."""

    # Get the list of installed games manifests
    MANIFESTS_PATH = "%ProgramData%\\Epic\\EpicGamesLauncher\\Data\\Manifests"
    manifest_files = Path(expandvars(MANIFESTS_PATH)).glob(".\\*.item")

    games = []
    for manifest_file in manifest_files:
        manifest = json_parse(open(manifest_file))

        # Prepare launcher url
        protocol = "com.epicgames.launcher://"
        base_path = "apps"
        namespace = manifest["CatalogNamespace"]
        id = manifest["CatalogItemId"]
        name = manifest["AppName"]
        query = urlencode({"action": "launch", "silent": "true"})
        path = quote(f"{base_path}/{namespace}:{id}:{name}")
        launcher_url = f"{protocol}{path}?{query}"

        # Prepare icon path
        install_path = manifest["InstallLocation"]
        icon_path = Path(install_path) / manifest["LaunchExecutable"]

        game = Game(platform="epic",
                    id=manifest["CatalogItemId"],
                    name=manifest["DisplayName"],
                    exe_path=launcher_url,
                    args="",
                    icon_path=icon_path)

        games.append(game)

    return games


# ----------------------------------------------------------------------
# Exports
# ----------------------------------------------------------------------
def get_installed_games():
    return _get_installed_gog_games() + _get_installed_epic_games()
