# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
import urllib.parse
from json import load as json_parse
from os import mkdir, path
from pathlib import Path
from time import sleep
from urllib import request

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
    except urllib.error.HTTPError as e:
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


# gog_games = {}
# gog_games_page = 1
# gog_games_total_pages = None
# while True:
#     url = urllib.parse.urljoin(
#         gogapi.urls.gog_servers["embed"],
#         gogapi.urls.web_config["account.get_filtered"],
#     ) + "?%s" % urllib.parse.urlencode({
#         "mediaType": 1,
#         "page": gog_games_page
#     })
#     body = gog_api.get_json(url)
#     if body["products"]:
#         for product in body["products"]:
#             gog_games[str(product["id"])] = product
#     gog_games_page += 1
#     gog_games_total_pages = body["totalPages"]
#     if gog_games_page > gog_games_total_pages:
#         break
# del gog_api, gog_games_page, gog_games_total_pages, url, body

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
#     steam_id = generate_steam_id(game.get_exe(), game.name, galaxy=False)
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

#     print(f"  - Downloaded grid: {game.name}")
#     cover_url = f'https:{gog_games[game.id]["image"]}.jpg'
#     request.urlretrieve(cover_url, download_path)
#     image_to_grid(download_path, grid_image_path)
#     sleep(0.5)
