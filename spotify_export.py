import json
import requests
import base64
import pprint
from types import SimpleNamespace

class SpotifyClient:

    def __init__(self, client_id, client_secret):
        # URLs
        self.SPOTIFY_API_URL = "https://api.spotify.com"
        self.SPOTIFY_ACCOUNTS_URL = "https://accounts.spotify.com/api/token"

        # ENDPOINTS
        self.GET_PLAYLIST = "/v1/playlists/{}"

        # HEADERS
        self.AUTHORIZATION_HEADER = "Authorization"

        self.base_headers = {
            self.AUTHORIZATION_HEADER: 'Bearer {}'.format(self.get_bearer_token(client_id, client_secret))
        }

    def get_bearer_token(self, client_id, client_secret):
        client_basic_combined = str(base64.b64encode('{}:{}'.format(client_id, client_secret).encode("utf-8")), "utf-8")

        basic_auth_request_headers = {
            self.AUTHORIZATION_HEADER: "Basic {}".format(client_basic_combined)
        }
        basic_auth_request_data = {
            'grant_type': 'client_credentials'
        }

        basic_auth_response = requests.post(self.SPOTIFY_ACCOUNTS_URL, data=basic_auth_request_data, verify=True,
                                            headers=basic_auth_request_headers)

        print("basic auth response status: {}".format(basic_auth_response.status_code))

        basic_auth_response_json = json.loads(basic_auth_response.text)

        # the access token
        access_token = basic_auth_response_json['access_token']

        return access_token

    def make_get_playlist_call(self, url, headers=None):
        if headers is None:
            headers = self.base_headers

        get_playlist_response = requests.get(url=url,headers=headers)

        return get_playlist_response

    def get_playlist(self,playlist_id):
        playlist_endpoint = self.GET_PLAYLIST.format(playlist_id)
        url = "".join([self.SPOTIFY_API_URL,playlist_endpoint])
        print("getting playlist at {}".format(url))

        get_playlist_response = self.make_get_playlist_call(url=url)

        get_playlist_response_json = json.loads(get_playlist_response.text, object_hook=lambda d: SimpleNamespace(**d))
        get_playlist_tracks_json = get_playlist_response_json.tracks

        while get_playlist_tracks_json.next is not None:
            next_url = get_playlist_tracks_json.next
            next_get_playlist_response = self.make_get_playlist_call(url=next_url)
            get_playlist_tracks_json = json.loads(next_get_playlist_response.text, object_hook=lambda d: SimpleNamespace(**d))

            playlist_items_results_json = get_playlist_tracks_json.items

            for item in playlist_items_results_json:
                get_playlist_response_json.tracks.items.append(item)
            get_playlist_response_json.tracks.next = get_playlist_tracks_json.next


        return get_playlist_response_json



