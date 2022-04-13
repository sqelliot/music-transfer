import unittest
import os
from spotify_export import SpotifyClient

class SpotifyClientTest(unittest.TestCase):

    def setUp(self):
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

        self.spotify_client = SpotifyClient(client_id=client_id,client_secret=client_secret)

        self.SQUELLIOTT_PLAYLIST_ID = "2wPnnLVEq3fBlEImHbyapg"

    def test_get_squelliott_playlist_200_response(self):

        playlist_json = self.spotify_client.get_playlist(self.SQUELLIOTT_PLAYLIST_ID)

        # self.assertEqual(200,playlist_json.status_code, "non 200 status code {}".format(playlist_json.reason))
        self.assertEqual(103,len(playlist_json.tracks.items))


if __name__ == '__main__':
    unittest.main()