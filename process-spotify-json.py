import json

with open ("spotify-export-playlist.json", "r") as json_file:
    spotify_json = json.load(json_file)

    items_array = spotify_json["tracks"]["items"]
    # print(tracks_array)

    # first song
    # for track_object_key, track_object_value in tracks_array[0].items():
    #     print(track_object_key,track_object_value)
    #     print()

    track_info_list = []
    for item in items_array:
        # get the track name
        # print(track)
        item_track_json = item["track"]
        track_info = {
            "source_artist_name": item_track_json["artists"][0]["name"],
            "source_track_name": item_track_json["name"],
            "source_album_name": item_track_json["album"]["name"]
        }
        track_info_list.append(track_info)
        # print(track_name)

    with open("playlist-info-tracking.json", mode='w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(track_info_list,indent=4,ensure_ascii=False))