# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from platform import system

from click import echo, group, option, pass_context, style

from atos import get_installed_games
from grid import get_gog_stats
from steam import (create_shortcut, get_user_ids, get_userdata_path,
                   load_shortcuts, save_shortcuts)
from util import (echo_debug, echo_error, echo_info,
                  truncate_default_shortcut_fields)


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def is_windows():
    return system() == "Windows"


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------
@group()
@option('--dry-run',
        default=False,
        is_flag=True,
        help="Don't save any changes to disk.")
@pass_context
def cli(ctx, dry_run):
    """AtoS: Steam shortcut manager"""
    ctx.obj = {"dry_run": dry_run}


@cli.command()
@pass_context
def sync_shortcuts(ctx):
    """Sync Steam shortcuts with installed games."""

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

    user_id = ids[0]
    echo_info(
        f"Syncing shortcuts for Steam user: {style(user_id, fg='green')}")

    echo()

    # load existing shortcuts
    existing_shortcuts = load_shortcuts(user_id)
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
            if shortcut['DevkitGameID'] == game.id:
                saved_last_play_time = shortcut.get("LastPlayTime", 0)
                if saved_last_play_time > 0:
                    last_play_time = saved_last_play_time
                    echo_debug(
                        f"Last play time restored for {style(game.name, fg='green')}"
                    )
                    break

        # create shortcut
        game_shortcut = create_shortcut(game.name,
                                        game.exe_path,
                                        icon=game.icon_path,
                                        launch_options=game.args,
                                        devkit_game_id=game.id,
                                        last_play_time=last_play_time,
                                        tags=[game.platform])
        echo_debug(f"{truncate_default_shortcut_fields(game_shortcut)}")

        # add to new shortcuts dictionary
        new_shortcuts[str(i)] = game_shortcut

    echo()

    # handle custom (user-created) shortcuts
    # Keep them as-is at the end of the list
    custom_shortcuts_count = 0
    for shortcut in existing_shortcuts.values():
        if shortcut['DevkitGameID'] not in [game.id for game in games]:
            new_shortcuts[str(len(new_shortcuts))] = shortcut
            custom_shortcuts_count += 1
            echo_debug(
                f"Custom shortcut for {style(shortcut['AppName'], fg='green')} added"
            )
    echo_info(
        f"{custom_shortcuts_count} custom shortcut(s) found and restored")

    # save new shortcuts
    if not ctx.obj["dry_run"]:
        save_shortcuts(user_id, {"shortcuts": new_shortcuts})
        echo_info("Saved new shortcuts")
    else:
        echo_info(f"{style('Dry run', fg='red')}: new shortcuts not saved")


@cli.command()
@option("--gog-username", required=True, help="Your GOG username.")
def download_grids(gog_username):
    """Download Steam grid images for current shortcuts"""

    # TODO: move handling of current steam id to group and pass it in
    # ctx

    # load shortcuts
    shortcuts = load_shortcuts()

    get_gog_stats(gog_username)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if not is_windows():
        echo_error(f"Unsupported OS: {style(system(), fg='green')}")
        exit(1)

    cli()
