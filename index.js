const fs = require('fs');
const path = require('path');
const GogGame = require('./lib/goggame');
const steamShortcuts = require('steam-shortcut-editor');


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
app.GOG_GAME_PATH = 'D:/games/_gog';

/**
 * App entry point
 */
app.main = function() {
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

  let shortcuts = games.map((game) => {
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
  shortcuts = {shortcuts};

  steamShortcuts.writeFile(
      app.getShortcutsPath, shortcuts, app.onShortcutWriteError
  );
};

/**
 * Generate the shortcuts file path
 * @return {string} The shortcuts file path
 */
app.getShortcutsPath = function() {
  return path.join(
      app.STEAM_INSTALL_PATH, 'userdata',
      app.STEAM_ID, 'config/shortcuts.vdf'
  );
};

/**
 * Handler for shortcut file writing errors.
 * @param {Error} error The writing error.
 */
app.onShortcutWriteError = function(error) {
  if (error) {
    throw new Error('Failed to write shortcuts file.');
  }
};


app.main();
