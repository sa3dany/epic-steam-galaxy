import re
import urllib.parse
import webbrowser
from os import mkdir, path
from pathlib import Path
from time import sleep
from urllib import request

import gogapi

from any.gog import get_gog_games
from any.epic import get_installed as get_epic_installed
from steam import (
    generate_steam_id,
    get_grid_images_path,
    image_to_grid,
    load_shortcuts,
    make_shortcut,
    save_shortcuts,
)
from util import unquote_string


if __name__ == "__main__":
    shortcuts = load_shortcuts("000000000")
    print(f"Parsed existing shortcuts.vdf")

    # Launcher Games
    gog_games = get_gog_games("C:\Program Files (x86)\GOG Galaxy\Games")
    print(f"Found {len(gog_games)} [GOG] installed games")

    epic_games = get_epic_installed()
    print(f"Found {len(epic_games)} [Epic] installed games")

    games = []
    games.extend(gog_games)
    games.extend(epic_games)

    new_shortcuts = {}
    for i, game in enumerate(games):
        new_shortcut = make_shortcut(
            id=game.id,
            exe=game.get_launcher_exe(),
            args=game.get_launcher_args(),
            pwd=game.get_pwd(),
            name=game.name,
            icon=game.get_exe(),
            tag=game.type,
        )
        new_shortcuts[str(i)] = new_shortcut

        for shortcut in shortcuts["shortcuts"].values():
            if (
                unquote_string(shortcut["Exe"]) == game.get_exe()
                or shortcut["AppName"] == game.name
                or shortcut["DevkitGameID"] == game.id
            ):
                if shortcut.get("LastPlayTime", 0) > 0:
                    new_shortcut["LastPlayTime"] = shortcut["LastPlayTime"]
                    print(f'  ☑ Restored LastPlayTime: {shortcut["AppName"]}')

    # Custom (user-created) shortcuts
    # Keep them at the end, don't modify them
    for shortcut in shortcuts["shortcuts"].values():
        if "GOG" in shortcut["tags"].values():
            continue
        if "EPIC" in shortcut["tags"].values():
            continue
        new_shortcuts[str(len(new_shortcuts))] = shortcut
        print("  ☐ Non-GOG: " + f'{shortcut["AppName"]}')

    # Save updated shortcuts
    save_shortcuts("000000000", {"shortcuts": new_shortcuts})
    print("Saved new shortcuts.vdf")

    exit(0)

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
