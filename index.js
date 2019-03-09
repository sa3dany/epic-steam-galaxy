const fs = require('fs');
const opn = require('opn');
const path = require('path');
const inquirer = require('inquirer');
const OAuth2 = require('client-oauth2');
const GogApi = require('./lib/gog-api');
const GogGame = require('./lib/gog-game');
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
      exe: game.getExePath(true),
      StartDir: game.getWorkingDir(),
      icon: game.getExePath(false),
      ShortcutPath: '',
      LaunchOptions: game.getArgs(),
      IsHidden: false,
      AllowDesktopConfig: false,
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
  /* shortcuts.writeFile(
      app.getShortcutsPath, gameShortcuts, app.onShortcutWriteError
  ); */

  // Write grid images
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

  const gog = new GogApi();
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
 * Handler for shortcut file writing errors.
 * @param {Error} error The writing error.
 */
app.onShortcutWriteError = (error) => {
  if (error) {
    throw new Error('Failed to write shortcuts file.');
  }
};


app.main();
