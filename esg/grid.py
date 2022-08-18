from json import load as json_parse
from urllib import request
from urllib.error import HTTPError


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
