# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from binascii import crc32
from pathlib import Path
from posixpath import expandvars

from PIL import Image
from resizeimage import resizeimage
from vdf import binary_dumps as vdf_dump
from vdf import binary_loads as vdf_load

from util import quote_string


# ----------------------------------------------------------------------
# Exports
# ----------------------------------------------------------------------
def get_profiles_path():
    """Get the path to the steam profiles folder."""

    path = expandvars("%ProgramFiles(x86)%\\Steam\\userdata")
    if not Path(path).exists():
        return None

    return path


def get_shortcuts_path(steamId):
    """Generate the shortcuts file path"""

    return "C:/Program Files (x86)/Steam/userdata" f"/{steamId}/config/shortcuts.vdf"


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
        pass


def get_grid_images_path(steamId):
    """Generate the Grid images folder path"""
    return "C:/Program Files (x86)/Steam/userdata" f"/{steamId}/config/grid"


def generate_steam_id(exe, name):
    """Generate an ID for a steam shortcut to use for naming grid images.
    The format of the string used to generate the ID used by Steam is:
    "{game_exe_path}"{game_name}

    Notice that the game_exe_path is quoted.

    https://github.com/Hafas/node-steam-shortcuts
    """

    input_string = f'"{exe}"{name}'
    top_32 = crc32(input_string.encode()) | 0x80000000
    return str(top_32) + "p"


def make_shortcut(id=None,
                  exe=None,
                  args=None,
                  pwd=None,
                  name=None,
                  icon=None,
                  tag=None):
    exe = quote_string(exe)
    pwd = quote_string(pwd)
    args = args
    return {
        "AppName": name,
        "Exe": exe,
        "StartDir": pwd,
        "icon": icon,
        "ShortcutPath": "",
        "LaunchOptions": args,
        "IsHidden": int(False),
        "AllowDesktopConfig": int(True),
        "AllowOverlay": int(True),
        "OpenVR": int(False),
        "Devkit": int(False),
        "DevkitGameID": id,
        "LastPlayTime": 0,
        "tags": dict([("0", tag)]) if tag else {},
    }


def image_to_grid(image_path, output_image_path):
    with open(image_path, "r+b") as f:
        with Image.open(f) as image:
            grid = resizeimage.resize_cover(image, [920, 430])
            grid.save(output_image_path, image.format)
