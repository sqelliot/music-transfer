var request = require('request');

var client_id = '';
var client_secret = '';
var redirect_uri = 'http://localhost:8888/callback';

// your application requests authorization
var authOptions = {
  url: 'https://accounts.spotify.com/api/token',
  headers: {
    'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
  },
  form: {
    grant_type: 'client_credentials'
  },
  json: true
};

request.post(authOptions, function(error, response, body) {
  if (!error && response.statusCode === 200) {

    // use the access token to access the Spotify Web API
    var token = body.access_token;
    console.log(token)
    var options = {
//      url: 'https://api.spotify.com/v1/users/sqelliott',
      url: 'https://api.spotify.com/v1/playlists/2wPnnLVEq3fBlEImHbyapg',
      headers: {
        'Authorization': 'Bearer ' + token
      },
      json: true
    };
    request.get(options, function(error, response, body) {
      console.log(body);
    });
  }
});


//request.post(authOptions, function(error, response, body) {
//  if (!error && response.statusCode === 200) {
//
//    // use the access token to access the Spotify Web API
//    var token = body.access_token;
//    var options = {
//      url: 'https://api.spotify.com/v1/me/tracks',
//      headers: {
//        'Authorization': 'Bearer ' + token
//      },
//      json: true
//    };
//    request.get(options, function(error, response, body) {
//      console.log(body);
//    });
//  }
//});
