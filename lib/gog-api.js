const rp = require('request-promise-native');
const OAuth2 = require('client-oauth2');

/**
 * The GOG API
 */
function Gog() {
  this.account = new GogAccount(this);
}

/**
 * Prepare API URLs.
 * @param {string} path
 * @param {string} func
 * @return {string} Full API call URL.
 */
Gog.prototype.prepareUrl = function(path, func) {
  return `https://embed.gog.com${path}/${func}`;
};

/**
 * Account related endpoints.
 * @param {Gog} gog GogApi instance.
 */
function GogAccount(gog) {
  this.gog_ = gog;
}

/**
 * Gog Account API path
 */
GogAccount.API_PATH = '/account';

/**
 * getFilteredProducts()
 * @param {Object} options
 * @return {Object}
 */
GogAccount.prototype.getFilteredProducts = function(options) {
  const token = options.auth;
  if (!(token instanceof OAuth2.Token)) {
    throw new Error('This endpoint requires a valid OAuth2 token.');
  }

  if (token.expired()) {
    throw new Error('Authentication tokan has expired.');
  }

  return rp(token.sign({
    json: true,
    qs: {
      mediaType: options.mediaType,
      page: options.page,
    },
    url: this.gog_.prepareUrl(GogAccount.API_PATH, 'getFilteredProducts'),
  }));
};


module.exports = Gog;
