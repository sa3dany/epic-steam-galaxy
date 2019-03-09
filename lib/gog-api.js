const fs = require('fs');
const opn = require('opn');
const request = require('request');
const {promisify} = require('util');
const readline = require('readline');
const OAuth2 = require('client-oauth2');
const querystring = require('querystring');

/**
 * The GOG API
 */
function Gog() {
  let credentials;

  try {
    credentials = fs.readFileSync('./credentials.json');
  } catch (e) {
    throw new Error('Missing credentials.json');
  }

  try {
    credentials = JSON.parse(credentials);
  } catch (e) {
    throw new Error('Cannot parse credentials.json');
  }

  this.oauth2_ = new OAuth2(credentials);
}

/**
 * getFilteredProducts()
 * @return {Object}
 */
Gog.prototype.getFilteredProducts = function() {
  if (!this.hasAccess()) {
    throw new Error('Not authenticated.');
  }
  const requestSync = promisify(request);
  const url = 'https://embed.gog.com/account/getFilteredProducts';
  const qs = {mediaType: 1};
  return requestSync(this.getToken().sign({url, qs}));
};

/**
 * Check is we have access using an access_token or atleast a refresh token
 * either in instance state or in local storage
 * @return {boolean}
 */
Gog.prototype.hasAccess = async function() {
  const token = this.getToken();
  if (token && !token.expired()) return true;
  if (token) {
    const newToken = await token.refresh();
    this.token_ = newToken;
  }
  return false;
};

/**
 * Get an authorization code to complete the OAuth2 flow and request an access
 * token. TODO: embed page in link that has javascript that can read the code.
 * @param {callback} callback The callback to call after recieving the
 *   authentication code
 */
Gog.prototype.authorize = function(callback) {
  opn(this.oauth_.code.getUri({
    query: {
      layout: 'client2',
    },
  }));
  const input = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  input.question('Paste the redirect URL:\n', (answer) => {
    input.close();
    this.authUrl_ = answer;
    this.getAccessToken();
    callback();
  });
};

/**
 * Retrieve access token.
 * @return {string} The authorization token.
 */
Gog.prototype.getAccessToken = async function() {
  const token = await this.oauth_.code.getToken(this.authUrl_);
  this.token_ = token;
  this.saveToken_(token);
};

/**
 * Get token from memory or disk if exists
 * @return {Object}
 */
Gog.prototype.getToken = function() {
  if (this.token_) return this.token_;
  const savedToken = this.loadToken_();
  if (savedToken) {
    this.token_ = savedToken;
    return savedToken;
  }
  return null;
};

/**
 * Save token to disk
 * @param {Object} token The OAuth2 token.
 */
Gog.prototype.saveToken_ = function(token) {
  fs.writeFileSync('./.gogrc.json', JSON.stringify({
    token: token.data,
    expires: token.expires.getTime(),
  }));
};

/**
 * Load token from disk
 * @return {Object} The token from disk.
 */
Gog.prototype.loadToken_ = function() {
  try {
    const rcFile = fs.readFileSync('./.gogrc.json');
    const rc = JSON.parse(rcFile);
    const token = this.oauth_.createToken(rc.token);
    token.expiresIn(new Date(rc.expires));
    return token;
  } catch (error) {
    return null;
  }
};


module.exports = Gog;
