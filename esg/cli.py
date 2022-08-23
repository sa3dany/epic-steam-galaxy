import logging
import platform
import sys
from pathlib import Path

import click

from esg.steam.profiles import SteamProfiles

from .steam.shortcuts import SteamShortcuts
from .util import get_steam_userdata_paths


# ----------------------------------------------------------------------
# CLI Commands
# ----------------------------------------------------------------------
@click.command()
@click.option(
    "-v",
    "verbose",
    help="Enable verbose output",
    is_flag=True,
)
@click.option(
    "--dry-run",
    help="Don't save changes to disk",
    is_flag=True,
)
@click.option(
    "--steam-userdata",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to Steam's userdata directory",
)
@click.option(
    "--gog-library",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to GOG's library directory",
)
@click.option(
    "--epic-manifests",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to EGL manifests directory",
)
@click.option(
    "--epic-clear-credentials",
    is_flag=True,
    help="Clear Epic credentials",
)
def cli(
    verbose: bool,
    dry_run: bool,
    steam_userdata: str | None,
    gog_library: str | None,
    epic_manifests: str | None,
    epic_clear_credentials: bool,
):
    # set logging level & format
    logging.basicConfig(
        style="{",
        format="{levelname}: {message}",
        level=logging.DEBUG if verbose else logging.INFO,
    )

    # At this point I know that if any dir path cli option is provided:
    #   - it exists
    #   - it is a dir

    try:
        steam_profiles = SteamProfiles(steam_userdata)
    except ValueError:
        logging.error(
            "Could not find your Steam `userdata` directory.\n"
            "Try the `--steam-userdata` option.",
        )
        exit(1)

    if steam_profiles.count() == 0:
        logging.error(
            "Could not find any Steam profiles.\n"
            "Try the `--steam-userdata` option.",
        )
        exit(1)

    if steam_profiles.count() > 1:
        click.echo("Multiple Steam profiles found:")
        for i, profile in enumerate(steam_profiles.list()):
            click.echo(f" {i+1}. {profile.name or profile.id}")
        profile_index = click.prompt(
            "Continue using profile",
            show_choices=True,
            type=click.Choice(
                [str(i + 1) for i in range(steam_profiles.count())]
            ),
        )
        steam_profile = steam_profiles.list()[int(profile_index) - 1]
    else:
        steam_profile = steam_profiles.list()[0]

    logging.info(f"Using Steam profile: {steam_profile.id}")
    logging.debug(f"Steam profile: {steam_profile}")

    # shortcuts = SteamShortcuts()


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    system_name = platform.system()

    if system_name != "Windows":
        click.secho(
            f"{system_name} is not supported.",
            err=True,
            fg="red",
        )
        exit(1)

    is_64bits = sys.maxsize > 2**32
    if not is_64bits:
        click.secho(
            "32-bit systems are not supported.",
            err=True,
            fg="red",
        )
        exit(1)

    cli()
