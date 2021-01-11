import requests
import re
import json

from bs4 import BeautifulSoup as bs


class AlbumDownloader(object):
    class Album(object):
        def __init__(self, playlist_id: str, title: str) -> None:
            self.playlist_id = playlist_id
            self.title = title

            super().__init__()
    
    class Track(object):
        ...

    @staticmethod
    def get_playlist_info(playlist_url: str):
        response = requests.get(playlist_url)

        if response.status_code != 200:
            return

        json_info = re.search(r"(?<=var ytInitialData = ).*?(?=;<\/script>)", response.text).group()
        json_info = json.loads(json_info)
        json_info = json_info["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]

        playlist_id = json_info["playlistId"]
        


album_downloader = AlbumDownloader()
album_downloader.get_playlist_info("https://www.youtube.com/playlist?list=PLGeJR8ZOrTZdMuBWM9IYta6IoHKku0nH4")