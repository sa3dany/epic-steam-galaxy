import logging
from multiprocessing.sharedctypes import Value
from pathlib import Path
from os.path import expandvars
from typing import NamedTuple

import vdf

DEFAULT_WINDOWS_USERDATA_PATH = expandvars(
    "%ProgramFiles(x86)%\\Steam\\userdata"
)


class Profile(NamedTuple):
    """Represents a Steam local user profile."""

    id: str
    name: str


class SteamProfiles:
    """Represents the collection of all local Steam profiles."""

    def __init__(self, userdata_path: str = None):
        userdata_path = Path(userdata_path or DEFAULT_WINDOWS_USERDATA_PATH)
        if not userdata_path.is_dir():
            raise NotADirectoryError(userdata_path)
        if not userdata_path.exists():
            raise ValueError(f"Directory does not exist: {userdata_path}")

        self._base_path = userdata_path
        self._users = []
        self._enumerate_users()

    def _enumerate_users(self):
        for user_path in self._base_path.iterdir():

            localconfig_path = user_path / "config" / "localconfig.vdf"

            if not user_path.is_dir():
                continue
            if not localconfig_path.exists():
                continue

            with open(localconfig_path, encoding="utf-8") as localconfig_file:
                localconfig = vdf.load(localconfig_file)

            profile_id = user_path.name
            profile_name = (
                localconfig.get("UserLocalConfigStore")
                .get("friends")
                .get("PersonaName")
            )

            if not profile_name:
                profile_name = ""
                logging.warn(
                    f"Could not lookup profile name for Steam ID: {profile_id}"
                )

            self._users.append(Profile(profile_id, profile_name))

    def count(self):
        return len(self._users)

    def list(self):
        return self._users
