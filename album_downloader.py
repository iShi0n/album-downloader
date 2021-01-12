import requests
import re
import json
from pprint import pprint

from bs4 import BeautifulSoup as bs


class AlbumDownloader(object):
    class Album(object):
        def __init__(self, playlist_id: str, title: str) -> None:
            self.playlist_id = playlist_id
            self.title = title

            super().__init__()
    
    class Track(object):
        def __init__(self, video_id: str, thumbnail: str, title: str) -> None:
            self.video_id = video_id
            self.title = title
            self.thumbnail = thumbnail
            self.url = "https://youtube.com/watch?v="+self.video_id
            super().__init__()

    @staticmethod
    def get_playlist_info(playlist_url: str):
        response = requests.get(playlist_url)

        if response.status_code != 200:
            return

        json_info = re.search(r"(?<=var ytInitialData = ).*?(?=;<\/script>)", response.text).group()
        json_info = json.loads(json_info)
        json_info = json_info["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]
        playlist_id = json_info["playlistId"]

        tracks = []

        for video in json_info["contents"]:
            video = video["playlistVideoRenderer"]
            
            video_title = video["title"]["runs"][0]["text"]
            video_id = video["videoId"]
            # Get the last thumbnail src. Last = better quality.
            video_thumbnail = video["thumbnail"]["thumbnails"][-1]["url"]

            tracks.append(AlbumDownloader.Track(video_id=video_id, title=video_title, thumbnail=video_thumbnail))

        response = requests.get(tracks[0].url)
        index = bs(response.text, 'html.parser')
        
        try:
            album_name = re.search(r"(?<=\"metadataRowRenderer\":{\"title\":{\"simpleText\":\".lbum\"},\"contents\":\[{\"simpleText\":\").*?(?=\"}])", response.text)
        except: 
            album_name = input("Nome do album não encontrado. Digite manualmente: ")



        


album_downloader = AlbumDownloader()
album_downloader.get_playlist_info("https://www.youtube.com/playlist?list=PLGeJR8ZOrTZdMuBWM9IYta6IoHKku0nH4")