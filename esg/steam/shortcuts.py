from os import PathLike
from pathlib import Path


class SteamShortcuts:
    def __init__(self, config_path: str | bytes | PathLike) -> None:
        shortcuts_path = Path(config_path) / "shortcuts.vdf"

        if not shortcuts_path.is_dir():
            raise IsADirectoryError(config_path)

        self._shortcuts_path = shortcuts_path
