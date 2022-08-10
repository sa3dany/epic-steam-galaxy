# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from json import load as json_parse
from os import mkdir, path
from pathlib import Path
from time import sleep
from urllib import request
from urllib.error import HTTPError

from steam import generate_steam_id, get_grid_images_path, image_to_grid


# ----------------------------------------------------------------------
# GOG.com
# ----------------------------------------------------------------------
def get_gog_stats(username):
    """Get the GOG.com stats for a user."""

    url = f"https://www.gog.com/u/{username}/games/stats"

    req = request.Request(url, method="GET")
    try:
        res = request.urlopen(req)
    except HTTPError as e:
        if e.code == 404:
            return None
        else:
            raise e

    stats_page = json_parse(res)

    stats = []
    stats += stats_page["_embedded"]["items"]

    while stats_page["_links"].get("next"):
        next_url = stats_page["_links"]["next"]["href"]
        req = request.Request(next_url, method="GET")
        res = request.urlopen(req)
        stats_page = json_parse(res)
        stats += stats_page["_embedded"]["items"]

    games = {}
    for item in stats:
        game = item["game"]
        games[game["id"]] = game
        del game["id"]

    return games


# ----------------------------------------------------------------------
# Epic Games
# ----------------------------------------------------------------------
# TODO: implement this

# try:
#     mkdir(get_grid_images_path("000000000"))
# except FileExistsError:
#     pass
# try:
#     mkdir(path.join(get_grid_images_path("000000000"), "gog"))
# except FileExistsError:
#     pass

# for game in games:
#     grid_path = get_grid_images_path("000000000")
#     steam_id = generate_steam_id(game.get_exe(), game.name)
#     grid_image_path = path.join(grid_path, f"{steam_id}.jpg")
#     download_path = path.join(grid_path, "gog", f"{game.id}.jpg")

#     if Path(grid_image_path).is_file():
#         continue

#     if Path(download_path).is_file():
#         print(f"  - Added grid from cache: {game.name}")
#         image_to_grid(download_path, grid_image_path)
#         continue

#     if not game.id in gog_games:
#         print(f"  - Not in GOG account: {game.name}")
#         continue

#     request.urlretrieve(cover_url, download_path)
#     image_to_grid(download_path, grid_image_path)
