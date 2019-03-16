const fs = require('fs');
const crc = require('crc');
const opn = require('opn');
const Long = require('long');
const path = require('path');
const sharp = require('sharp');
const {promisify} = require('util');
const inquirer = require('inquirer');
const OAuth2 = require('client-oauth2');
const GogApi = require('./lib/gog-api');
const Bottleneck = require('bottleneck');
const GogGame = require('./lib/gog-game');
const rp = require('request-promise-native');
const shortcuts = require('steam-shortcut-editor');


/**
 * Main app object
 */
const app = {};

/**
 * The steam user ID. Used for the path for the shortcuts file
 */
app.STEAM_ID = '280467180';

/**
 * The steam installation directory
 */
app.STEAM_INSTALL_PATH = 'C:/Program Files (x86)/Steam';

/**
 * GOG Installation directory
 */
app.GOG_INSTALL_PATH = 'C:/Program Files (x86)/GOG Galaxy';

/**
 * GOG game install path
 */
app.GOG_GAME_PATH = 'G:/games/_gog';

/**
 * App entry point
 */
app.main = async () => {
  const gameDirs = fs.readdirSync(app.GOG_GAME_PATH)
      .filter((dirName) => {
        const dirPath = path.join(app.GOG_GAME_PATH, dirName);
        return fs.statSync(dirPath).isDirectory();
      });

  const games = [];
  gameDirs.forEach((dirName) => {
    const dirPath = path.join(app.GOG_GAME_PATH, dirName);
    try {
      games.push(new GogGame(dirPath));
    } catch (e) {
      // A non-game directory
    }
  });

  let gameShortcuts = games.map((game) => {
    return {
      AppName: game.name,
      exe: game.getExePath(),
      StartDir: game.getWorkingDir(),
      icon: game.getExePath(),
      ShortcutPath: '',
      LaunchOptions: game.getArgs(),
      IsHidden: false,
      AllowDesktopConfig: true,
      AllowOverlay: true,
      OpenVR: false,
      DevKit: false,
      DevKitGameID: '',
      LastPlayTime: 0,
      tags: ['GOG'],
    };
  });
  gameShortcuts = {gameShortcuts};

  // Write shortcuts
  console.log(`Writing shortcuts file for ${games.length} GOG games`);
  shortcuts.writeFile(
      app.getShortcutsPath(), gameShortcuts, app.onShortcutWriteError
  );

  // Authorize with GOG
  console.log('Authorizing with gog.com.');
  const gogAuthClient = new OAuth2(app.getGogCredentials());
  let token = app.loadToken(gogAuthClient);
  if (!token) {
    const gogAuth = await app.getGogAuthorization(gogAuthClient);
    token = await gogAuthClient.code.getToken(gogAuth.uri);
    app.saveGogToken(token);
  } else if (token.expired()) {
    token = await token.refresh();
    app.saveGogToken(token);
  }

  // Get all the account's games
  console.log('Getting game data for your GOG games.');
  const gog = new GogApi();
  const gogAccountGamesMap = {};
  let gogAccountGamesPage = 1;
  let gogAccountGamesTotalPages;
  do {
    let body;
    try {
      body = await gog.account.getFilteredProducts({
        auth: token,
        mediaType: 1,
        page: gogAccountGamesPage,
      });
    } catch (e) {
      throw e;
    }
    if (body.products) {
      body.products.forEach((product) => {
        gogAccountGamesMap[product.id] = product;
      });
    }
    gogAccountGamesPage += 1;
    gogAccountGamesTotalPages = body.totalPages;
  } while (gogAccountGamesPage <= gogAccountGamesTotalPages);

  // Download game images if they don't exits
  console.log('Downloading steam GRID images.');
  try {
    fs.mkdirSync(path.join(app.getGridImagesPath(), 'originals'));
  } catch (e) {
    if (e.code !== 'EEXIST') throw (e);
  }

  const limiter = new Bottleneck({maxConcurrent: 1, minTime: 1000});

  const gamesToProcess = games.filter((game) => {
    const steamId = app.generateSteamAppId(game.name, game.getExePath());
    try {
      fs.accessSync(path.join(app.getGridImagesPath(), `${steamId}.jpg`));
      return false;
    } catch (e) {
      return true;
    }
  });

  gamesToProcess.forEach(async (game) => {
    const steamId = app.generateSteamAppId(game.name, game.getExePath());
    const gridPath = app.getGridImagesPath();
    const gridCachePath = path.join(gridPath, 'originals');
    const finalImgPath = path.join(gridPath, `${steamId}.jpg`);
    const imagePath = path.join(gridCachePath, `${game.gameId}.jpg`);
    let image;
    try {
      image = fs.readFileSync(imagePath);
      console.log(`  Found cached image: ${game.name}`);
      await sharp(image)
          .resize(920, 430)
          .jpeg({quality: 95})
          .toFile(finalImgPath);
      return;
    } catch (e) {
      // empty
    }

    const gogGame = gogAccountGamesMap[game.gameId];
    if (!gogGame) {
      throw new Error(`${game.name} not found in your GOG account.`);
    }

    image = await rp(`https:${gogGame.image}.jpg`, {encoding: null});
    console.log(`  Downloaded image: ${game.name}`);
    fs.writeFileSync(imagePath, image);
    await sharp(image)
        .resize(920, 430)
        .jpeg({quality: 95})
        .toFile(finalImgPath);
  });
};

/**
 * Load GOG API token from disk
 * @param {OAuth2} client The OAuth2 client.
 * @return {OAuth2.Token|null} The GOG API OAuth2 token or null if no saved
 *    token found.
 */
app.loadToken = (client) => {
  const tokenPath = path.join(__dirname, '.gogrc.json');
  let tokenFile;
  try {
    tokenFile = fs.readFileSync(tokenPath);
  } catch (e) {
    return null;
  }
  let tokenData;
  try {
    tokenData = JSON.parse(tokenFile);
  } catch (e) {
    throw new Error('Cannot parse saved token.');
  }
  const token = client.createToken(tokenData.token);
  token.expiresIn(new Date(tokenData.expires));
  return token;
};

/**
 * Save GOG API token to disk.
 * @param {OAuth2.Token} token The OAuth2 token.
 */
app.saveGogToken = (token) => {
  const tokenPath = path.join(__dirname, '.gogrc.json');
  try {
    fs.writeFileSync(tokenPath, JSON.stringify({
      token: token.data,
      expires: token.expires.getTime(),
    }));
  } catch (e) {
    throw new Error('Failed to save GOG OAuth2 token.');
  }
};

/**
 * Open a browser window to get the authentication code for an OAuth2 flow.
 * @param {OAuth2} client The OAuth2 client.
 * @return {Promise}
 */
app.getGogAuthorization = (client) => {
  opn(client.code.getUri({query: {layout: 'client2'}})), {wait: false};
  return inquirer.prompt([{
    name: 'uri',
    message: 'Redirect URI:',
  }]);
};

/**
 * Read credentials file and return its parsed contents (token).
 * @return {Object}
 */
app.getGogCredentials = () => {
  const file = path.join(__dirname, 'credentials.json');
  let credentials;
  try {
    credentials = fs.readFileSync(file);
  } catch (e) {
    throw new Error('Missing credentials.json');
  }
  try {
    credentials = JSON.parse(credentials);
  } catch (e) {
    throw new Error('Cannot parse credentials.json');
  }
  return credentials;
};

/**
 * Generate an ID for a steam shrtcut to use for naming grid images.
 * @see https://github.com/Hafas/node-steam-shortcuts
 * @param {string} name
 * @param {srting} exe
 * @return {string} The generated ID.
 */
app.generateSteamAppId = function(name, exe) {
  const crcValue = crc.crc32(`${exe}` + name);
  let longValue = new Long(crcValue, crcValue, true);
  longValue = longValue.or(0x80000000);
  longValue = longValue.shl(32);
  longValue = longValue.or(0x02000000);
  return longValue.toString();
};

/**
 * Read existing shortcuts from disk
 * @return {Object} The parsed shortcuts from disk.
 */
app.loadShortcuts = function() {
  const parse = promisify(shortcuts.parseFile);
  return parse(app.getShortcutsPath(), {
    autoConvertArrays: true,
    autoConvertBooleans: true,
    dateProperties: ['LastPlayTime'],
  });
};

/**
 * Generate the shortcuts file path
 * @return {string} The shortcuts file path
 */
app.getShortcutsPath = () => {
  return path.join(
      app.STEAM_INSTALL_PATH, 'userdata',
      app.STEAM_ID, 'config/shortcuts.vdf'
  );
};

/**
 * Generate the Grid images folder path
 * @return {string} The grid images folder path
 */
app.getGridImagesPath = () => {
  return path.join(
      app.STEAM_INSTALL_PATH, 'userdata',
      app.STEAM_ID, 'config/grid'
  );
};

/**
 * Handler for shortcut file writing errors.
 * @param {Error} error The writing error.
 */
app.onShortcutWriteError = (error) => {
  if (error) {
    throw new Error('Failed to write shortcuts file.');
  }
};


app.main();
