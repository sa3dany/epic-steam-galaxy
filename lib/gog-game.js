const fs = require('fs');
const path = require('path');


/**
 * Returns a new GogGame instance.
 * @param {string} gamePath The game directory path.
 * @constructor
 */
function GogGame(gamePath) {
  const isGogInfo = RegExp.prototype.test.bind(/goggame-[0-9]+\.info/i);
  const files = fs.readdirSync(gamePath).filter(isGogInfo);
  if (!files.length) {
    throw new Error(
        `Could not initilaize instance with path: "${gamePath}". `
      + 'No info file found.'
    );
  }

  const gogInfoPath = path.join(gamePath, files[0]);
  const gogInfoFile = fs.readFileSync(gogInfoPath);
  const gogInfo = JSON.parse(gogInfoFile);

  this.gamePath_ = gamePath;
  this.playTasks_ = gogInfo.playTasks;

  this.gameId = gogInfo.gameId;
  this.name = gogInfo.name;
}

GogGame.prototype.getPrimaryPlayTask = function() {
  const primaryTasks = this.playTasks_.filter((task) => (task.isPrimary));
  if (primaryTasks.length !== 1) {
    throw new Error(
        `Expected only 1 primary play task. Found: ${primaryTasks.length}`
    );
  }
  return primaryTasks[0];
};

/**
 * Get the executable path of the game.
 * @return {string} The game executable path.
 */
GogGame.prototype.getExePath = function() {
  const primaryTask = this.getPrimaryPlayTask();
  return path.join(this.gamePath_, primaryTask.path);
};

/**
 * Get the Arguments (if-any) of the primary play task.
 * @return {string} The game arguments.
 */
GogGame.prototype.getArgs = function() {
  const primaryTask = this.getPrimaryPlayTask();
  return primaryTask.arguments;
};

/**
 * Get the game executable's working directory.
 * @return {string} The game exe working directory.
 */
GogGame.prototype.getWorkingDir = function() {
  const primaryTask = this.getPrimaryPlayTask();
  if (primaryTask.workingDir) {
    return path.join(this.gamePath_, primaryTask.workingDir);
  } else {
    return this.gamePath_;
  }
};

/**
 * Get the path for the ico file of the game.
 * @return {string} The .ico file path.
 */
GogGame.prototype.getIconPath = function() {
  const iconFile = `goggame-${this.gameId}.ico`;
  return path.join(this.gamePath_, iconFile);
};

/**
 * Get the commandline arguments to lauch the game through GOG Galaxy.
 * @return {string} GOG Galaxy command line arguments to launch the game.
 */
GogGame.prototype.getRunCommand = function() {
  return `/command=runGame `
       + `/gameId=${this.gameId} `
       + `/path="${this.getWorkingDir()}"`;
};


module.exports = GogGame;
