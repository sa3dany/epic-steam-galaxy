from json import loads as json_parse
from os.path import expandvars
from pathlib import Path


def get_username():
    """Get username."""

    GALAXY_LOCAL_CONFIG_PATH = (
        "%LocalAppData%\\GOG.com\\Galaxy\\Configuration\\config.json"
    )

    config_file = Path(expandvars(GALAXY_LOCAL_CONFIG_PATH))
    if not config_file.exists():
        return None

    config = json_parse(config_file.read_text())
    return config.get("username", None)
