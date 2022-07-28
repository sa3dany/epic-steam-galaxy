from binascii import crc32

import vdf
from PIL import Image
from resizeimage import resizeimage

from util import quote_string


def get_shortcuts_path(steamId):
    """Generate the shortcuts file path"""

    return "C:/Program Files (x86)/Steam/userdata" f"/{steamId}/config/shortcuts.vdf"


def load_shortcuts(steamId: str) -> dict:
    """Load shortcuts.vdf from disk."""

    try:
        vdf_file = open(get_shortcuts_path(steamId), "rb")
        shortcuts = vdf.binary_loads(vdf_file.read())
    except FileNotFoundError:
        shortcuts = {"shortcuts": {}}
    return shortcuts


def save_shortcuts(steamId, shortcuts):
    """Save shortcuts.vdf to disk"""

    vdf_file = open(get_shortcuts_path(steamId), "wb")
    vdf_bytes = vdf.binary_dumps(shortcuts)
    bytes_written = vdf_file.write(vdf_bytes)
    if bytes_written != len(vdf_bytes):
        pass


def get_grid_images_path(steamId):
    """Generate the Grid images folder path"""
    return "C:/Program Files (x86)/Steam/userdata" f"/{steamId}/config/grid"


def generate_steam_id(game, galaxy=False):
    """Generate an ID for a steam shortcut to use for naming grid images.
    https://github.com/Hafas/node-steam-shortcuts
    """

    # if galaxy:
    #     input_string = f'"{get_galaxy_exe()}"{game.name}'
    # else:
    input_string = f'"{game.get_exe()}"{game.name}'
    top_32 = crc32(input_string.encode()) | 0x80000000
    return str(top_32) + "p"


def make_shortcut(game, galaxy=False):
    # if galaxy:
    #     exe = quote_string(get_galaxy_exe())
    #     pwd = quote_string(get_galaxy_path())
    #     icon = game.get_exe()
    #     args = game.get_galaxy_args()
    # else:
    exe = quote_string(game.get_exe())
    pwd = quote_string(game.get_pwd())
    icon = ""
    args = game.get_args()
    return {
        "AppName": game.name,
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
        "DevkitGameID": game.id,
        "LastPlayTime": 0,
        "tags": dict([("0", "GOG")]),
    }


def image_to_grid(image_path, output_image_path):
    with open(image_path, "r+b") as f:
        with Image.open(f) as image:
            grid = resizeimage.resize_cover(image, [920, 430])
            grid.save(output_image_path, image.format)
