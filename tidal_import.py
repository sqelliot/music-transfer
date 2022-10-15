import requests
import urllib.parse
import json
import time
import os


class TidalClient:

    def __init__(self):
        self.access_code = os.environ["TIDAL_ACCESS_CODE"]

        self.tidal_api_url = "https://api.tidal.com"
        self.tidal_listen_url = "https://listen.tidal.com"
        self.tidal_create_playlist_url = self.tidal_api_url + "/v2/my-collection/playlists/folders/create-playlist"
        self.tidal_query_url = self.tidal_listen_url + "/v1/search/top-hits"
        self.tidal_add_to_playlist_base_url = self.tidal_listen_url + "/v1/playlists"

        self.base_headers = {
            'Authorization': 'Bearer ' + self.access_code,
            'content-type': 'application/json',
            'accept': '*/*'
        }
        self.base_parameters = {
            "countryCode": "US",
            "locale": "en_US"
        }

        self.tidal_playlist_id = None

        self.DESTINATION_TRACK_ID_KEY = "destination_track_id"

    def get_root_playlists_folder(self):
        root_playlists_response = requests.get(
            "https://api.tidal.com/v2/my-collection/playlists/folders?folderId=root&includeOnly=&offset=0&limit=50"
            "&order=DATE&orderDirection=DESC&countryCode=US&locale=en_US&deviceType=BROWSER",
            headers=self.base_headers)
        response_text_json = json.loads(root_playlists_response.text)
        return response_text_json

    def does_playlist_name_exist(self, playlist_name):
        root_playlists_json = self.get_root_playlists_folder()
        playlists_items = root_playlists_json["items"]
        # print(playlists_items)
        for item in playlists_items:
            if playlist_name == item["name"]:
                if self.tidal_playlist_id is None:
                    self.tidal_playlist_id = item["data"]["uuid"]
                return True
        return False

    def playlist_etag(self):
        tidal_playlist_url = self.tidal_add_to_playlist_base_url + "/" + self.tidal_playlist_id + "/items"

        headers = self.base_headers
        headers.update({'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})

        playlist_response = requests.get(tidal_playlist_url, headers=headers, params=self.base_parameters)
        # print(playlist_response)

        return playlist_response.headers["etag"]

    def query_track_info(self, track_info):
        accept_language_pair = {'accept-language': 'en,en-GB;q=0.9,en-US;q=0.8'}
        query_request_headers = self.base_headers
        query_request_headers.update(accept_language_pair)

        query = " ".join([track_info["source_artist_name"], track_info["source_track_name"]])
        print("query: {}".format(query))

        query_request_parameters = {
            "query": query,
            "limit": 1,
            "offset": 0,
            "types": "TRACKS"
        }

        parameters = self.base_parameters
        parameters.update(query_request_parameters)
        # print(tidal_query_url)
        # print(query_request_headers)
        # print(parameters)

        query_response = requests.get(self.tidal_query_url, headers=query_request_headers, params=parameters)

        if query_response.status_code != 200:
            response_info = {
                "code": query_response.status_code,
                "reason": query_response.reason
            }
            print("response info: ".format(response_info))

        return query_response

    def get_track_json(self, track):
        track_info = {
            self.DESTINATION_TRACK_ID_KEY: None
        }

        print()
        print("=========================================================")
        print("Getting track info for query: " + str(track))
        query_response = self.query_track_info(track)
        items = query_response.json()["tracks"]["items"]
        if len(items) == 0:
            print("no tracks returned")
        else:
            track_json = items[0]

            # guarantee that source and destination artist names are equal
            destination_artist_name = track_json["artists"][0]["name"]
            if destination_artist_name == track["source_artist_name"]:
                track_info = {
                    "destination_track_name": track_json["title"],
                    "destination_artist_name": destination_artist_name,
                    self.DESTINATION_TRACK_ID_KEY: track_json["id"]
                }

                print("Track info: {}".format(str(track_info)))
            else:
                print("artists didn't match")
                track_info.update({"bad_match_artist": destination_artist_name})

        return track_info

    def get_track_list_ids(self, track_list, use_cache=True):
        track_list_ids = []
        track_list_info_updated = False
        for track in track_list:
            # check if already have id
            if self.DESTINATION_TRACK_ID_KEY in track.keys() and use_cache:
                track_id = track[self.DESTINATION_TRACK_ID_KEY]
            else:
                track_list_info_updated = True
                track_info = self.get_track_json(track)
                track.update(track_info)
                track_id = track_info[self.DESTINATION_TRACK_ID_KEY]

            if track_id is not None:
                track_list_ids.append(track_id)

        if track_list_info_updated:
            with open(self.PLAYLIST_INFO_JSON_FILE_NAME, "w") as playlist_info_file:
                playlist_info_file.write(json.dumps(track_list, indent=4, ensure_ascii=False))
        return track_list_ids

    def get_track_list_to_import(self):
        with open(self.PLAYLIST_INFO_JSON_FILE_NAME, "r") as tracks_file:
            return json.load(tracks_file)

    def add_songs_to_playlist(self,id_list, bulk_import=True):
        tidal_add_to_playlist_full_url = self.tidal_add_to_playlist_base_url + "/" + self.tidal_playlist_id + "/items"

        headers = self.base_headers
        headers.update({'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        headers.update({'if-none-match': self.playlist_etag()})

        if bulk_import:
            data = {
                'onArtifactNotFound': "FAIL",
                'onDupes': "SKIP",
                'trackIds': id_list
            }

            add_track_to_playlist_response = requests.post(tidal_add_to_playlist_full_url, headers=self.base_headers,
                                                           data=data)
        else:
            for id in id_list:
                headers.update({'if-none-match': self.playlist_etag()})
                data = {
                    'onArtifactNotFound': "FAIL",
                    'onDupes': "SKIP",
                    'trackIds': id
                }

                add_track_to_playlist_response = requests.post(tidal_add_to_playlist_full_url, headers=self.base_headers,
                                                               data=data)
                print(add_track_to_playlist_response)

        return add_track_to_playlist_response

    def create_playlist(self, playlist_name):

        # check if playlist name exists
        if self.does_playlist_name_exist(playlist_name):
            print("playlist name: " + playlist_name + "already exists")
            return

        create_playlist_parameters = {
            "description": "",
            "folderId": "root",
            "name": playlist_name
        }
        parameters = self.base_parameters
        parameters.update(create_playlist_parameters)

        parameters_encoded = urllib.parse.urlencode(parameters)

        # create playlist
        create_playlist_response = requests.put(self.tidal_create_playlist_url + "?" + parameters_encoded,
                                                headers=self.base_headers)

        create_playlist_response_code = create_playlist_response.status_code
        print(create_playlist_response_code)
        self.tidal_playlist_id = create_playlist_response.json()["data"]["uuid"]

        return create_playlist_response


def main():
    print()
    tidal_client = TidalClient()
    tidal_client.create_playlist()
    track_list = tidal_client.get_track_list_to_import()


def tidal_import():
    tidal_client = TidalClient()
    tidal_client.create_playlist()
    track_list = tidal_client.get_track_list_to_import()
    track_ids_list = tidal_client.get_track_list_ids(track_list)
    print(track_ids_list)
    response = tidal_client.add_songs_to_playlist(track_ids_list, bulk_import=False)
    print(response)


if __name__ == "__main__":
    main()
