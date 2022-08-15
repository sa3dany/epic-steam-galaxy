# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from binascii import crc32
from os.path import expandvars
from pathlib import Path

from PIL import Image
from resizeimage import resizeimage
from vdf import binary_dumps as vdf_dump
from vdf import binary_loads as vdf_load


# ----------------------------------------------------------------------
# Exports
# ----------------------------------------------------------------------
def get_userdata_path():
    """Get the path to the steam userdata directory."""

    path = expandvars("%ProgramFiles(x86)%\\Steam\\userdata")
    if not Path(path).exists():
        return None

    return path


def get_shortcuts_path(steamId):
    """Get the path to a user's `shortcuts.vdf` file path"""

    userdata_path = get_userdata_path()
    if not userdata_path:
        raise ValueError("Userdata path does not exist.")

    return Path(userdata_path) / steamId / "config" / "shortcuts.vdf"


def get_grids_path(steamId):
    """Get the path to a user's grid images path"""

    userdata_path = get_userdata_path()
    if not userdata_path:
        raise ValueError("Userdata path does not exist.")

    return Path(userdata_path) / steamId / "config" / "grid"


def get_user_ids(userdata_path):
    """Get the Steam users (profiles) IDs on the system."""

    if not userdata_path:
        raise ValueError("Userdata path is required.")

    userdata_path = Path(userdata_path)
    if not userdata_path.exists():
        raise ValueError("Userdata path does not exist.")
    if not userdata_path.is_dir():
        raise ValueError("Userdata path is not a directory.")

    # filter to just the directories that contain a localconfig.vdf file
    user_profiles = [
        x for x in userdata_path.iterdir()
        if x.is_dir() and (x / "config" / "localconfig.vdf").exists()
    ]

    return [profile.name for profile in user_profiles]


def create_shortcut(app_name,
                    exe,
                    app_id="",
                    start_dir="",
                    icon="",
                    shortcut_path="",
                    launch_options="",
                    is_hidden=False,
                    allow_desktop_config=True,
                    allow_overlay=True,
                    open_vr=False,
                    devkit=False,
                    devkit_game_id="",
                    devkit_override_app_id=False,
                    last_play_time=0,
                    flatpak_app_id="",
                    tags=[]):
    """Create a shortcut dictionary for Steam."""

    if not app_name:
        raise ValueError("app_name is required.")
    if not exe:
        raise ValueError("An exe path is required.")

    # The `Exe`, `StartDir` and other paths must be quoted.
    return {
        "appid": app_id,  # appears to be random
        "AppName": app_name,
        "Exe": f'"{exe}"' if exe else "",
        "StartDir": f'"{start_dir}"' if start_dir else "",
        "icon": f'"{icon}"' if icon else "",
        "ShortcutPath": f'"{shortcut_path}"' if shortcut_path else "",
        "LaunchOptions": launch_options,
        "IsHidden": int(is_hidden),
        "AllowDesktopConfig": int(allow_desktop_config),
        "AllowOverlay": int(allow_overlay),
        "OpenVR": int(open_vr),
        "Devkit": int(devkit),
        "DevkitGameID": devkit_game_id,
        "DevkitOverrideAppID": int(devkit_override_app_id),
        "LastPlayTime": last_play_time,
        "FlatpakAppID": flatpak_app_id,
        "tags": {str(i): tags[i]
                 for i in range(len(tags))} if len(tags) else {},
    }


def load_shortcuts(steamId: str) -> dict:
    """Load shortcuts.vdf from disk."""

    try:
        vdf_file = open(get_shortcuts_path(steamId), "rb")
        shortcuts = vdf_load(vdf_file.read())
    except FileNotFoundError:
        shortcuts = {"shortcuts": {}}
    return shortcuts


def save_shortcuts(steamId, shortcuts):
    """Save shortcuts.vdf to disk"""

    vdf_file = open(get_shortcuts_path(steamId), "wb")
    vdf_bytes = vdf_dump(shortcuts)
    bytes_written = vdf_file.write(vdf_bytes)
    if bytes_written != len(vdf_bytes):
        raise ValueError("Failed to write all bytes to file.")


def generate_old_steam_id(exe, name):
    """Generate an ID for a steam shortcut to use for naming grid images.
    The format of the string used to generate the ID used by Steam is:
    "{game_exe_path}"{game_name}

    Notice that the game_exe_path is quoted.

    https://github.com/Hafas/node-steam-shortcuts
    """

    input_string = f'"{exe}"{name}'
    top_32 = crc32(input_string.encode()) | 0x80000000
    full_64 = (top_32 << 32) | 0x02000000
    return str(full_64)


def generate_steam_id(exe, name):
    """Generate an ID for a steam shortcut to use for naming grid
    images. Uses the new format for the new steam library. Does not
    apply to big picture mode yet.
    """

    input_string = f'"{exe}"{name}'
    top_32 = crc32(input_string.encode()) | 0x80000000
    return str(top_32) + "p"


def image_to_grid(image_path, output_image_path):
    with open(image_path, "r+b") as f:
        with Image.open(f) as image:
            grid = resizeimage.resize_cover(image, [920, 430])
            grid.save(output_image_path, image.format)
