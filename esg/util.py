# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from click import echo, style


# ----------------------------------------------------------------------
# Output functions
# ----------------------------------------------------------------------
def echo_error(message):
    echo(f"[{style('error', fg='red')}] {message}", err=True)


def echo_info(message):
    echo(f"[{style('info', fg='blue')}] {message}")


def echo_debug(message):
    echo(f"[{style('debug', fg='magenta')}] {message}")


# ----------------------------------------------------------------------
# String functions
# ----------------------------------------------------------------------
def unquote_string(quoted_string):
    return quoted_string[1:-1]


# ----------------------------------------------------------------------
# Debug functions
# ----------------------------------------------------------------------
def truncate_default_shortcut_fields(shortcut: dict) -> dict:
    """Truncate default shortcut fields to reduce noise in logs"""

    truncated_shortcut = {}

    for key, value in shortcut.items():
        if key in ["appid", "AppName", "Exe"]:
            truncated_shortcut[key] = value

        elif key in [
                "StartDir", "icon", "ShortcutPath", "LaunchOptions",
                "DevkitGameID", "FlatpakAppID"
        ]:
            if value:
                truncated_shortcut[key] = value

        elif key in ["IsHidden", "OpenVR", "Devkit", "DevkitOverrideAppID"]:
            if value == 1:
                truncated_shortcut[key] = value

        elif key in ["AllowDesktopConfig", "AllowOverlay"]:
            if value == 0:
                truncated_shortcut[key] = value

        elif key == "LastPlayTime":
            if value > 0:
                truncated_shortcut[key] = value

        elif key == "tags":
            if len(value.items()):
                truncated_shortcut[key] = value

        else:
            truncated_shortcut[key] = value

    return truncated_shortcut
