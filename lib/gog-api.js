const fs = require('fs');
const opn = require('opn');
const {promisify} = require('util');
const request = require('request');
const readline = require('readline');
const querystring = require('querystring');
const OAuth2 = require('client-oauth2');

/**
 * Initialise a GOG API instance.
 */
function Gog() {
  this.oauth_ = new OAuth2(Gog.CREDENTIALS);
}

/**
 * GOG CLient Credentials.
 * @type {string}
 */
Gog.CREDENTIALS = JSON.parse(fs.readFileSync('./credentials.json'));

/**
 * Check is we have access using an access_token or atleast a refresh token
 * either in instance state or in local storage
 * @return {boolean}
 */
Gog.prototype.hasAccess = function() {
  if (this.token_) {
    return true;
  }
  let savedToken;
  try {
    savedToken = JSON.parse(fs.readFileSync('./gogrc.json'));
    this.token_ = savedToken;
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Get an authorization code to complete the OAuth2 flow and request an access
 * token. TODO: embed page in link that has javascript that can read the code.
 * @param {callback} callback The callback to call after recieving the
 *   authentication code
 */
Gog.prototype.authorize = function() {
  opn(this.oauth_.code.getUri({
    query: {
      layout: 'client2',
    },
  }));

  const input = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  input.question[promisify.custom] = (question) => {
    return new Promise((resolve) => {
      input.question(question, resolve);
    });
  };

  const questionSync = promisify(input.question).bind(input);
  this.authCode_ = await questionSync('Paste the authorization code:\n');
  input.close();
};

/**
 * Retrieve access token.
 * @return {string} The authorization token.
 */
Gog.prototype.getAccessToken = async function() {
  const query = querystring.stringify({
    client_id: Gog.CLIENT_ID,
    client_secret: Gog.CLIENT_SECRET,
    grant_type: 'authorization_code',
    code: this.authCode_,
    redirect_uri: 'https://embed.gog.com/on_login_success?origin=client',
  });

  const requestSync = promisify(request.post);
  const responce = await requestSync(`https://auth.gog.com/token`, {
    form: query,
  });
  this.token_ = responce.body;
  fs.writeFileSync('./gogrc.json', JSON.stringify(responce.body));
};

const gog = new Gog();
gog.authorize(onAuth);
