import json
import requests
import base64

TRACKS_KEY="tracks"
ITEMS_KEY="items"
client_id = ''
client_secret = ''
client_basic_combined = str(base64.b64encode(str(client_id + ':' + client_secret).encode("utf-8")),"utf-8")
# print(client_basic_combined)
redirect_uri = 'http://localhost:8888/callback'
data = { 'grant_type': 'client_credentials'}

auth_url = 'https://accounts.spotify.com/api/token'
## squelliont playlist
spotify_playlist_url ='https://api.spotify.com/v1/playlists/2wPnnLVEq3fBlEImHbyapg'

auth_response = requests.post(auth_url, data=data, verify=True, headers={"Authorization": "Basic " + client_basic_combined})

token_json = json.loads(auth_response.text)
# print(token_json)

# the access token
access_token = token_json['access_token']

authorization_header_value= 'Bearer ' + access_token


spotify_playlist_response = requests.get(spotify_playlist_url, headers={'Authorization': authorization_header_value})

playlist_results_json = spotify_playlist_response.json()
playlist_track_results_json = playlist_results_json[TRACKS_KEY]


while playlist_track_results_json["next"] is not None:
    print("getting next tracks from playlist")
    spotify_playlist_response = requests.get(playlist_track_results_json["next"], headers={'Authorization': authorization_header_value})
    playlist_track_results_json = spotify_playlist_response.json()
    playlist_items_results_json = playlist_track_results_json[ITEMS_KEY]

    print(len(spotify_playlist_response.json()[ITEMS_KEY]))
    for item in playlist_items_results_json:
        playlist_results_json[TRACKS_KEY][ITEMS_KEY].append(item)

# print("spotify playstlist GET response: " + str(spotify_playlist_response.status_code))
# print("playlist GET response: " + spotify_playlist_response["statusCode"])

# write to file
with open("spotify-export-playlist.json", "w") as outfile:
    print("Totally items in final json:  " + str(len(playlist_results_json[TRACKS_KEY][ITEMS_KEY])))
    json.dump(playlist_results_json, outfile, indent=4,ensure_ascii=False)

