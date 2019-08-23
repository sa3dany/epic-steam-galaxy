import re
import json
import os.path
import webbrowser
import urllib.parse
from os import path
from os import mkdir
from os import getenv
from time import sleep
from pathlib import Path
from urllib import request
from binascii import crc32

import vdf
import gogapi
from PIL import Image
from resizeimage import resizeimage

from goggame import GogGame


def get_gog_games(path):
    '''Get GOG games.'''

    games = []
    info_files = Path(path).glob('./*/goggame-*.info')
    for info_file in info_files:
        game = GogGame(info_file)
        if not game.is_dlc:
            games.append(game)
    return games


def get_galaxy_path():
    '''Get the GOG Galaxy client install path'''

    programfiles = os.getenv('programfiles(x86)')
    return os.path.join(programfiles, 'GOG Galaxy')


def get_galaxy_exe():
    '''Get the GOG Galaxy client exe path'''

    programfiles = os.getenv('programfiles(x86)')
    return os.path.join(programfiles, 'GOG Galaxy', 'GalaxyClient.exe')


def get_shortcuts_path(steamId):
    '''Generate the shortcuts file path'''

    return ('C:/Program Files (x86)/Steam/userdata'
            f'/{steamId}/config/shortcuts.vdf')


def load_shortcuts(steamId: str) -> dict:
    '''Load shortcuts.vdf from disk.'''

    vdf_file = open(get_shortcuts_path(steamId), 'rb')
    shortcuts = vdf.binary_loads(vdf_file.read())
    return shortcuts


def save_shortcuts(steamId, shortcuts):
    '''Save shortcuts.vdf to disk'''

    vdf_file = open(get_shortcuts_path(steamId), 'wb')
    vdf_bytes = vdf.binary_dumps(shortcuts)
    bytes_written = vdf_file.write(vdf_bytes)
    if bytes_written != len(vdf_bytes):
        pass


def quote_string(string):
    return '"' + string + '"'


def unquote_string(quoted_string):
    return quoted_string[1:-1]


def get_grid_images_path(steamId):
    '''Generate the Grid images folder path'''
    return ('C:/Program Files (x86)/Steam/userdata'
            f'/{steamId}/config/grid')


def generate_steam_id(game, galaxy=False):
    '''Generate an ID for a steam shrtcut to use for naming grid images.
    https://github.com/Hafas/node-steam-shortcuts
    '''

    if galaxy:
        input_string = f'"{get_galaxy_exe()}"{game.name}'
    else:
        input_string = f'"{game.get_exe()}"{game.name}'
    top_32 = crc32(input_string.encode()) | 0x80000000
    full_64 = (top_32 << 32) | 0x02000000
    return str(full_64)


def image_to_grid(image_path, ouput_image_path):
    with open(image_path, 'r+b') as f:
        with Image.open(f) as image:
            grid = resizeimage.resize_cover(image, [920, 430])
            grid.save(ouput_image_path, image.format)


def make_shortcut(game, galaxy=False):
    if galaxy:
        exe = quote_string(get_galaxy_exe())
        pwd = quote_string(get_galaxy_path())
        icon = game.get_exe()
        args = game.get_galaxy_args()
    else:
        exe = quote_string(game.get_exe())
        pwd = quote_string(game.get_pwd())
        icon = ''
        args = game.get_args()
    return {
        'AppName': game.name,
        'Exe': exe,
        'StartDir': pwd,
        'icon': icon,
        'ShortcutPath': '',
        'LaunchOptions': args,
        'IsHidden': int(False),
        'AllowDesktopConfig': int(True),
        'AllowOverlay': int(True),
        'OpenVR': int(False),
        'DevKit': int(False),
        'DevKitGameID': game.id,
        'LastPlayTime': 0,
        'tags': dict([('0', 'GOG')]),
    }


print('----------------------------------------')
print('Generating new shortcuts.vdf')
print('----------------------------------------')

games = get_gog_games('G:/games/_gog')
print(f'Found {len(games)} installed games')

shortcuts = load_shortcuts('000000000')
print(f'Parsed existing shortcuts.vdf')

new_shortcuts = dict(shortcuts={})
for i, game in enumerate(games):
    last_play_time = 0
    for key, shortcut in shortcuts['shortcuts'].items():
        if (unquote_string(shortcut['Exe']) == game.get_exe()
            or shortcut['AppName'] == game.name
            or shortcut['DevKitGameID'] == game.id):
            last_play_time = shortcut['LastPlayTime']
    new_shortcut = make_shortcut(game, galaxy=False)
    if last_play_time > 0:
        new_shortcut['LastPlayTime'] = last_play_time
        print(f'  ☑ Restored LastPlayTime: {shortcut["AppName"]}')
    new_shortcuts['shortcuts'][str(i)] = new_shortcut
del i, game

gog_shortcuts_len = len(new_shortcuts) + 1
for i, shortcut in shortcuts['shortcuts'].items():
    is_gog_shortcut = False
    if 'tags' in shortcut:
        for key, tag in shortcut['tags'].items():
            if tag == 'GOG':
                is_gog_shortcut = True
    if not is_gog_shortcut:
        print('  ☐ Non-GOG: ' + f'{shortcut["AppName"]}')
        new_shortcuts['shortcuts'][str(gog_shortcuts_len + int(i))] = shortcut

save_shortcuts('000000000', new_shortcuts)
print('Saved new shortcuts.vdf\n')

print('----------------------------------------')
print('Applying GRID images')
print('----------------------------------------')

try:
    token = gogapi.Token.from_file('.gogrc.json')
    if token.expired():
        token.refresh()
        token.save('.gogrc.json')
except:
    webbrowser.open(gogapi.get_auth_url(), new=2, autoraise=True)
    print(f'''\
    Your web browser has been opened to allow you to log in.
    If that did not work, please manually open {gogapi.get_auth_url()}
    After completing the login you will be redirected to a blank page.
    Copy the full URL starting with
    https://embed.gog.com/on_login_success and paste it into this
    window.
    ''')

    login_url = input('Login URL: ')
    code_match = re.compile(r'code=([\w\-]+)').search(login_url)
    if code_match is None:
        print('Error: Could not find a login code in the provided URL')
        exit(1)

    token = gogapi.Token.from_code(code_match.group(1))
    token.save('.gogrc.json')
    del login_url, code_match

gog_api = gogapi.GogApi(token)
gog_games = {}
gog_games_page = 1
gog_games_total_pages = None
while True:
    url = urllib.parse.urljoin(
        gogapi.urls.gog_servers['embed'],
        gogapi.urls.web_config['account.get_filtered']
    ) + '?%s' % urllib.parse.urlencode(
        {'mediaType': 1,
         'page': gog_games_page}
    )
    body = gog_api.get_json(url)
    if body['products']:
        for product in body['products']:
            gog_games[str(product['id'])] = product
    gog_games_page += 1
    gog_games_total_pages = body['totalPages']
    if gog_games_page > gog_games_total_pages:
        break
del gog_api, gog_games_page, gog_games_total_pages, url, body
print(f'Found {len(gog_games)} GOG games in your account')

try:
    os.mkdir(os.path.join(get_grid_images_path('000000000'), 'gog'))
except FileExistsError:
    pass

for game in games:
    grid_path = get_grid_images_path('000000000')
    steam_id = generate_steam_id(game, galaxy=False)
    grid_image_path = path.join(grid_path, f'{steam_id}.jpg')
    download_path = path.join(grid_path, 'gog', f'{game.id}.jpg')

    if Path(grid_image_path).is_file():
        continue

    if Path(download_path).is_file():
        print(f'  - Added grid from cache: {game.name}')
        image_to_grid(download_path, grid_image_path)
        continue

    if not game.id in gog_games:
        print(f'  - Not in GOG account: {game.name}')
        continue

    print(f'  - Downloaded grid: {game.name}')
    cover_url = f'https:{gog_games[game.id]["image"]}.jpg'
    request.urlretrieve(cover_url, download_path)
    image_to_grid(download_path, grid_image_path)
    sleep(0.5)
