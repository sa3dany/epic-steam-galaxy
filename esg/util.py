from click import echo, secho, style


def echo_error(message):
    secho(f"{message}", err=True, fg="red")


def echo_info(message):
    echo(f"[{style('info', fg='blue')}] {message}")


def echo_debug(message):
    echo(f"[{style('debug', fg='magenta')}] {message}")


def unquote_string(quoted_string):
    return quoted_string[1:-1]


def truncate_default_shortcut_fields(shortcut: dict) -> dict:
    """Truncate default shortcut fields to reduce noise in logs"""

    truncated_shortcut = {}

    for key, value in shortcut.items():
        if key in ["appid", "AppName", "Exe"]:
            truncated_shortcut[key] = value

        elif key in [
            "StartDir",
            "icon",
            "ShortcutPath",
            "LaunchOptions",
            "DevkitGameID",
            "FlatpakAppID",
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
