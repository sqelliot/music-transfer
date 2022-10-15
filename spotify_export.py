import json
import requests
import base64
import os

from pymongo import MongoClient


def store_playlist_json(playlist_json):
    playlist_name = playlist_json["name"]
    playlist_id = playlist_json["id"]

    playlist_file_name = "{}_{}{}".format(playlist_name, playlist_id, ".json")

    with open(playlist_file_name, "w") as playlist_file:
        playlist_file.write(json.dumps(playlist_json, indent=4, ensure_ascii=False))



class SpotifyClient:

    def __init__(self, client_id=None, client_secret=None):
        if client_id is None or client_secret is None:
            client_id = os.environ["SPOTIFY_CLIENT_ID"]
            client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

        # URLs
        self.SPOTIFY_API_URL = "https://api.spotify.com"
        self.SPOTIFY_ACCOUNTS_URL = "https://accounts.spotify.com/api/token"

        '''
        ENDPOINTS
        '''
        # USER

        # PLAYLISTS
        self.GET_PLAYLIST = "/v1/playlists/{}"
        self.GET_CURRENT_USERS_PLAYLISTS = "/me/playlists"
        self.GET_USERS_PLAYLISTS = "/users/{}/playlists"

        # HEADERS
        self.AUTHORIZATION_HEADER = "Authorization"

        self.base_headers = {
            self.AUTHORIZATION_HEADER: 'Bearer {}'.format(self.get_bearer_token(client_id, client_secret))
        }

    def get_bearer_token(self, client_id, client_secret):
        client_combined = client_id + ":" + client_secret
        client_basic_combined = str(base64.b64encode(client_combined.encode("utf-8")), "utf-8")

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

    def form_full_api_url(self, endpoint):
        full_url = "".join([self.SPOTIFY_API_URL, endpoint])
        print("full_url: {}".format(full_url))

        return full_url

    def make_get_playlist_call(self, url, headers=None):
        if headers is None:
            headers = self.base_headers

        get_playlist_response = requests.get(url=url, headers=headers)

        return get_playlist_response

    def get_playlist(self, playlist_id):
        playlist_endpoint = self.GET_PLAYLIST.format(playlist_id)
        url = self.form_full_api_url(playlist_endpoint)
        print("getting playlist at {}".format(url))

        get_playlist_response = self.make_get_playlist_call(url=url)

        # get_playlist_response_json = json.loads(get_playlist_response.text, object_hook=lambda d: SimpleNamespace(**d))
        get_playlist_response_json = get_playlist_response.json()
        get_playlist_tracks_json = get_playlist_response_json["tracks"]

        while get_playlist_tracks_json["next"] is not None:
            next_url = get_playlist_tracks_json["next"]
            next_get_playlist_response = self.make_get_playlist_call(url=next_url)
            # get_playlist_tracks_json = json.loads(next_get_playlist_response.text, object_hook=lambda d: SimpleNamespace(**d))
            get_playlist_tracks_json = next_get_playlist_response.json()

            playlist_items_results_json = get_playlist_tracks_json["items"]

            for item in playlist_items_results_json:
                get_playlist_response_json["tracks"]["items"].append(item)
            get_playlist_response_json["tracks"]["next"] = get_playlist_tracks_json["next"]

        return get_playlist_response_json

    def get_current_users_playlists(self):
        url = self.form_full_api_url(self.GET_CURRENT_USERS_PLAYLISTS)

        get_current_users_playlists_response = requests.get(url, headers=self.base_headers)

        return get_current_users_playlists_response


class MusicTransferClient:

    def __init__(self):
        self.DATABASE_HOST = 'mongodb://localhost:27017'
        self.DATABASE_NAME = 'music_transfer'

        self.SPOTIFY_TRACKS_COLLECTION = 'spotify_tracks'

        self.music_transfer_db_client = MongoClient(self.DATABASE_HOST + '/' + self.DATABASE_NAME)[self.DATABASE_NAME]
        self.spotify_tracks_client = self.music_transfer_db_client[self.SPOTIFY_TRACKS_COLLECTION]

    def store_spotify_track(self, spotify_track_json):
        spotify_track_id = spotify_track_json['id']

        spotify_track_document = {
            'spotify_id': spotify_track_id,
            'spotify_track': spotify_track_json
        }

        self.spotify_tracks_client.insert_one(spotify_track_document)


class Squelliott(SpotifyClient):

    def __init__(self):
        self.SQUELLIOTT_PLAYLIST_ID = "2wPnnLVEq3fBlEImHbyapg"
        self.SQUELLIOTT_PLAYLIST_NAME = "Squelliott"
