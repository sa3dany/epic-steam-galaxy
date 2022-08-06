import re
import urllib.parse
import webbrowser
from os import mkdir, path
from pathlib import Path
from time import sleep
from urllib import request

import gogapi

from steam import generate_steam_id, get_grid_images_path, image_to_grid

try:
    token = gogapi.Token.from_file(".gogrc.json")
    if token.expired():
        token.refresh()
        token.save(".gogrc.json")
except:
    webbrowser.open(gogapi.get_auth_url(), new=2, autoraise=True)
    print(
        f"""\
    Your web browser has been opened to allow you to log in.
    If that did not work, please manually open {gogapi.get_auth_url()}
    After completing the login you will be redirected to a blank page.
    Copy the full URL starting with
    https://embed.gog.com/on_login_success and paste it into this
    window.
    """
    )

    login_url = input("Login URL: ")
    code_match = re.compile(r"code=([\w\-]+)").search(login_url)
    if code_match is None:
        print("Error: Could not find a login code in the provided URL")
        exit(1)

    token = gogapi.Token.from_code(code_match.group(1))
    token.save(".gogrc.json")
    del login_url, code_match

gog_api = gogapi.GogApi(token)
gog_games = {}
gog_games_page = 1
gog_games_total_pages = None
while True:
    url = urllib.parse.urljoin(
        gogapi.urls.gog_servers["embed"],
        gogapi.urls.web_config["account.get_filtered"],
    ) + "?%s" % urllib.parse.urlencode({"mediaType": 1, "page": gog_games_page})
    body = gog_api.get_json(url)
    if body["products"]:
        for product in body["products"]:
            gog_games[str(product["id"])] = product
    gog_games_page += 1
    gog_games_total_pages = body["totalPages"]
    if gog_games_page > gog_games_total_pages:
        break
del gog_api, gog_games_page, gog_games_total_pages, url, body

try:
    mkdir(get_grid_images_path("000000000"))
except FileExistsError:
    pass
try:
    mkdir(path.join(get_grid_images_path("000000000"), "gog"))
except FileExistsError:
    pass

for game in games:
    grid_path = get_grid_images_path("000000000")
    steam_id = generate_steam_id(game.get_exe(), game.name, galaxy=False)
    grid_image_path = path.join(grid_path, f"{steam_id}.jpg")
    download_path = path.join(grid_path, "gog", f"{game.id}.jpg")

    if Path(grid_image_path).is_file():
        continue

    if Path(download_path).is_file():
        print(f"  - Added grid from cache: {game.name}")
        image_to_grid(download_path, grid_image_path)
        continue

    if not game.id in gog_games:
        print(f"  - Not in GOG account: {game.name}")
        continue

    print(f"  - Downloaded grid: {game.name}")
    cover_url = f'https:{gog_games[game.id]["image"]}.jpg'
    request.urlretrieve(cover_url, download_path)
    image_to_grid(download_path, grid_image_path)
    sleep(0.5)
