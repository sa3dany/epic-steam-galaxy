import logging
import platform
import sys
from pathlib import Path
from typing import List

import click
import psutil

from .steam.profiles import Profile, SteamProfiles
from .steam.shortcuts import SteamShortcuts


# ----------------------------------------------------------------------
#  Helpers
# ----------------------------------------------------------------------
def get_steam_process_info() -> psutil.Process | None:
    steam_process = None
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"] == "steam.exe":
            return proc
    if not steam_process:
        return None


def wait_process_end(process: psutil.Process) -> None:
    try:
        psutil.wait_procs([process])
    except KeyboardInterrupt:
        exit(1)


def prompt_steam_profile(steam_profiles: List[Profile]) -> Profile:
    for i, profile in enumerate(steam_profiles.list()):
        click.echo(f" {i+1}. {profile.name or profile.id}")
        profile_index = click.prompt(
            "Continue using profile",
            show_choices=True,
            type=click.Choice(
                [str(i + 1) for i in range(steam_profiles.count())]
            ),
        )
        return steam_profiles.list()[int(profile_index) - 1]


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
    # ---------------------------------- setup app-wide logging defaults
    logging.basicConfig(
        style="{",
        format="{levelname}: {message}",
        level=logging.DEBUG if verbose else logging.INFO,
    )

    # ------------------------------------------- verify os requirements
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

    # ------------------------------------------- Steam already running?
    steam_process = get_steam_process_info()
    if steam_process:
        logging.warning("Steam is currently running")
        click.echo("Please exit Steam to continue ...")
        wait_process_end(steam_process)

    # ------------------------------------------------ Get Steam profile
    steam_profile = None
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

    if steam_profiles.count() == 1:
        steam_profile = steam_profiles.list()[0]

    elif steam_profiles.count() > 1:
        click.echo("Multiple Steam profiles found:")
        steam_profile = prompt_steam_profile(steam_profiles)

    logging.info(f"Using Steam profile: {steam_profile.id}")
    logging.debug(f"Steam profile: {steam_profile}")

    # shortcuts = SteamShortcuts()


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    cli()
