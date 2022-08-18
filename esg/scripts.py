# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from os import mkdir, system
from pathlib import Path
from platform import system
from urllib.request import urlretrieve

from click import echo, group, option, pass_context, style
from legendary.core import LegendaryCore
from legendary.models.exceptions import InvalidCredentialsError

from esg.grid import get_gog_stats
from esg.main import get_installed_games
from esg.platforms import gog
from esg.steam import (
    create_shortcut,
    generate_old_steam_id,
    generate_steam_id,
    get_grids_path,
    get_user_ids,
    get_userdata_path,
    image_to_grid,
    load_shortcuts,
    save_shortcuts,
)
from esg.util import (
    echo_debug,
    echo_error,
    echo_info,
    truncate_default_shortcut_fields,
    unquote_string,
)


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def is_windows():
    return system() == "Windows"


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------
@group()
@option(
    "--dry-run",
    default=False,
    is_flag=True,
    help="Don't save any changes to disk.",
)
@pass_context
def cli(ctx, dry_run):
    """Epic Steam Galaxy: Non-Steam game shortcut manager"""

    # Get steam's profiles path
    userdata_path = get_userdata_path()
    if not userdata_path:
        echo_error("Could not find Steam's profiles path")
        exit(1)

    # Get the list of users on the system
    ids = get_user_ids(userdata_path)

    # if more than one user, error out for now
    if len(ids) > 1:
        echo_error("Multiple Steam users are not supported yet")
        exit(1)

    # TODO: log steam user id selected

    ctx.obj = {}
    ctx.obj["dry_run"] = dry_run
    ctx.obj["steam_id"] = ids[0]


@cli.command()
@pass_context
def sync_shortcuts(ctx):
    """Sync Steam shortcuts with installed games."""

    # get the steam ID from current context
    steam_id = ctx.obj["steam_id"]
    echo_info(
        f"Syncing shortcuts for Steam user: {style(steam_id, fg='green')}"
    )

    echo()

    # load existing shortcuts
    existing_shortcuts = load_shortcuts(steam_id)
    existing_shortcuts = existing_shortcuts["shortcuts"]
    echo_info(f"Loaded {len(existing_shortcuts)} existing shortcut(s)")
    for i, shortcut in existing_shortcuts.items():
        echo_debug(f"{i}: {truncate_default_shortcut_fields(shortcut)}")

    echo()

    # Get installed games
    games = get_installed_games()
    echo_info(f"Found {len(games)} installed game(s)")

    # prepare new shortcuts dictionary
    new_shortcuts = {}

    # Build new shortcuts dictionary
    for i, game in enumerate(games):
        echo_info(f" - {style(game.platform, fg='yellow')} {game.name}")

        # get last play time from existing shortcuts if available
        last_play_time = 0
        for shortcut in existing_shortcuts.values():
            if shortcut["DevkitGameID"] == game.id:
                saved_last_play_time = shortcut.get("LastPlayTime", 0)
                if saved_last_play_time > 0:
                    last_play_time = saved_last_play_time
                    echo_debug(
                        f"Last play time restored for {style(game.name, fg='green')}"
                    )
                    break

        # create shortcut
        game_shortcut = create_shortcut(
            game.name,
            game.exe_path,
            icon=game.icon_path,
            launch_options=game.args,
            devkit_game_id=game.id,
            last_play_time=last_play_time,
            tags=[game.platform],
        )
        echo_debug(f"{truncate_default_shortcut_fields(game_shortcut)}")

        # add to new shortcuts dictionary
        new_shortcuts[str(i)] = game_shortcut

    echo()

    # handle custom (user-created) shortcuts
    # Keep them as-is at the end of the list
    custom_shortcuts_count = 0
    for shortcut in existing_shortcuts.values():
        if shortcut["DevkitGameID"] not in [game.id for game in games]:
            new_shortcuts[str(len(new_shortcuts))] = shortcut
            custom_shortcuts_count += 1
            echo_debug(
                f"Custom shortcut for {style(shortcut['AppName'], fg='green')} added"
            )
    echo_info(f"{custom_shortcuts_count} custom shortcut(s) found and restored")

    # save new shortcuts
    if not ctx.obj["dry_run"]:
        save_shortcuts(steam_id, {"shortcuts": new_shortcuts})
        echo_info("Saved new shortcuts")
    else:
        echo_info(f"{style('Dry run', fg='red')}: new shortcuts not saved")


@cli.command()
@option("--gog-username", required=False, help="Your GOG username.")
@pass_context
def download_grids(ctx, gog_username):
    """Download Steam grid images for current shortcuts."""

    # try to get username from Galaxy config
    if not gog_username:
        gog_username = gog.get_username()
        if not gog_username:
            echo_error("Could not find GOG username")
            exit(1)

    # load shortcuts
    steam_id = ctx.obj["steam_id"]
    shortcuts = load_shortcuts(steam_id)

    # find the platform tags used in the shortcuts
    platforms = set()
    for shortcut in shortcuts["shortcuts"].values():
        first_tag = shortcut["tags"].get("0", None)
        if first_tag:
            platforms.add(first_tag)
    echo_info(f"Found {len(platforms)} platform(s): {', '.join(platforms)}")

    echo()

    grids_path = get_grids_path(steam_id)
    cache_path = str(Path(grids_path) / "esg-cache")

    # make sure these directories exist
    if not ctx.obj["dry_run"]:
        try:
            mkdir(grids_path)
            echo_debug(f"Created {grids_path}")
        except FileExistsError:
            echo_debug(
                f"grids dir: {style(grids_path, fg='yellow')} already exists"
            )
        try:
            mkdir(cache_path)
            echo_debug(f"Created {cache_path}")
        except FileExistsError:
            echo_debug(
                f"cache dir: {style(cache_path, fg='yellow')} already exists"
            )

    echo()

    # download grids for each platform
    # TODO: refactor the reusable code across platforms
    if "gog" in platforms:
        echo_info(f"Getting grids for {style('gog', fg='green')}")

        # get gog stats
        echo_info(f"Downloading stats for {style(gog_username, fg='green')}")
        games = get_gog_stats(gog_username)

        # get grids
        echo_info(f"Downloading grids for {style('gog', fg='green')}")
        for shortcut in shortcuts["shortcuts"].values():
            if shortcut["tags"].get("0", "") != "gog":
                continue

            game_id = shortcut["DevkitGameID"]
            old_steam_id = generate_old_steam_id(
                unquote_string(shortcut["Exe"]), shortcut["AppName"]
            )
            steam_id = generate_steam_id(
                unquote_string(shortcut["Exe"]), shortcut["AppName"]
            )

            game = games.get(game_id, None)
            if not game:
                echo_error(f"No stats found for {shortcut['AppName']}")
                continue

            echo_info(f" - {shortcut['AppName']}")

            source_image_url = game["image"]
            source_image_path = Path(cache_path) / f"{game_id}.jpg"
            grid_paths = [
                Path(grids_path) / f"{steam_id}.jpg",
                Path(grids_path) / f"{old_steam_id}.jpg",
            ]

            for grid_path in grid_paths:
                if grid_path.is_file():
                    echo_debug(
                        f"Grid image {style(grid_path, fg='yellow')} already exists"
                    )
                    continue

                if source_image_path.is_file():
                    echo_debug(
                        f"Source image {style(source_image_path, fg='yellow')} already exists"
                    )
                    if not ctx.obj["dry_run"]:
                        image_to_grid(source_image_path, str(grid_path))
                    continue

                if not ctx.obj["dry_run"]:
                    urlretrieve(source_image_url, str(source_image_path))
                    image_to_grid(source_image_path, str(grid_path))

                # TODO: 2652489558_hero.png (steam client cover images (wide))

                echo_debug(f"Source image url: {source_image_url}")
                echo_debug(f"Source image path: {source_image_path}")
                echo_debug(f"Grid image path: {grid_path}")

    echo()

    if "epic" in platforms:
        echo_info(f"Getting grids for {style('epic', fg='green')}")

        # Prepare the legendary core
        legendary = LegendaryCore()
        try:
            if not legendary.login():
                echo_error("Could not log in to Epic")
        except ValueError:
            pass
        except InvalidCredentialsError:
            legendary.lgd.invalidate_userdata()

        # Grab the list of games in user's library
        games = legendary.egs.get_library_items()

        # get grids
        echo_info(f"Downloading grids for {style('epic', fg='green')}")
        for shortcut in shortcuts["shortcuts"].values():
            if shortcut["tags"].get("0", "") != "epic":
                continue

            game_id = shortcut["DevkitGameID"]
            steam_id = generate_steam_id(
                unquote_string(shortcut["Exe"]), shortcut["AppName"]
            )

            echo_info(f" - {shortcut['AppName']}")

            source_image_path = Path(cache_path) / f"{game_id}.jpg"
            grid_image_path = Path(grids_path) / f"{steam_id}.jpg"
            grid_paths = [
                Path(grids_path) / f"{steam_id}.jpg",
                Path(grids_path) / f"{old_steam_id}.jpg",
            ]

            for grid_path in grid_paths:
                if grid_path.is_file():
                    echo_debug(
                        f"Grid image {style(grid_path, fg='yellow')} already exists"
                    )
                    continue

                if source_image_path.is_file():
                    echo_debug(
                        f"Source image {style(source_image_path, fg='yellow')} already exists"
                    )
                    if not ctx.obj["dry_run"]:
                        image_to_grid(source_image_path, str(grid_path))
                    continue

                # Get the game image URLs
                source_image_url = None
                for game in games:
                    if game["catalogItemId"] != game_id:
                        continue
                    game_info = legendary.egs.get_game_info(
                        namespace=game["namespace"],
                        catalog_item_id=game_id,
                    )
                    key_images = game_info["keyImages"]
                    for key_image in key_images:
                        if "Tall" not in key_image["type"]:
                            source_image_url = key_image["url"]
                            break

                if not ctx.obj["dry_run"]:
                    urlretrieve(source_image_url, str(source_image_path))
                    image_to_grid(source_image_path, str(grid_path))


# ----------------------------------------------------------------------
# Module entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Currently only Windows x64 is supported
    os_name = system()
    if os_name != "Windows":
        echo_error(f"{os_name} is currently unsupported.")
        exit(1)

    cli()
