import os
import requests
import re
import json
from pprint import pprint

import eyed3
from pytube import YouTube #TODO: try to make it manually
from bs4 import BeautifulSoup as bs


class YouTube(object):
    class Track(object):
        def __init__(self, video_id: str, thumbnail: str, title: str) -> None:
            self.video_id = video_id
            self.title = title
            self.thumbnail_src = thumbnail
            self.thumbnail = requests.get(self.thumbnail_src).content
            self.url = "https://youtube.com/watch?v="+self.video_id
            self.mp3_src = YouTube(self.url).streams.get_audio_only("webm").url

            self.mp3_filename = f"{self.title}.mp3"

        def __dict__(self):
            return {"video_id": self.video_id, "title": self.title, "thumbnail": self.thumbnail_src, "url": self.url}

        def __repr__(self):
            return str(self.__dict__())

        def download(self, album_title: str):
            try:
                os.mkdir(album_title)
            except FileExistsError:
                pass
            except Exception as e:
                exit(str(e))

            self.mp3_full_path = f"{album_title}/{self.mp3_filename}"

            with open(self.mp3_full_path, "wb") as mp3_file:
                mp3_content = requests.get(self.mp3_src).content
                mp3_file.write(mp3_content)
                mp3_file.close()

            self.set_metadata(album_title, remove_from_title="bladee - ")

        def _get_artist(self) -> str:
            response = requests.get(self.url)

            try:
                artist_name = re.search(r"(?<=\"metadataRowRenderer\":{\"title\":{\"simpleText\":\"Artista\"},\"contents\":\[{\"simpleText\":\").*?(?=\"}])", response.text).group() #TODO: tentar capturar Artist e Artista. (caso esteja em outra linguagem)
            except:
                artist_name = input("[x]Nome do artista não encontrado. Digite manualmente: ")

            return artist_name

        def set_metadata(self, album_title, remove_from_title=""):
            title = self.title.replace(remove_from_title, "")
            
            # try:
            #     mp3_file = EasyID3(self.mp3_full_path)
            # except:
            #     mp3_file = mutagen.File(self.mp3_full_path, easy=True)
            
            
            mp3_file = eyed3.load(self.mp3_full_path)
            
            mp3_file.initTag()

            mp3_file.tag.artist = self._get_artist()
            mp3_file.tag.album = album_title
            mp3_file.tag.save()

            # mp3_file.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=album_title, data=self.thumbnail))
            # mp3_file.tags.add(TALB(encoding=3, text=title))
            # mp3_file.tags.add(TALB(encoding=3, text=album_title))
            # mp3_file.tags.add(TPE1(encoding=3, text=self._get_artist()))
            # mp3_file.save(self.mp3_full_path)


    class Album(object):
        def __init__(self, playlist_id: str, title: str, tracks: "Track") -> None:
            self.playlist_id = playlist_id
            self.title = title
            self.tracks = tracks
            self.url = "https://youtube.com/playlist?list="+self.playlist_id

            super().__init__()

        def __dict__(self):
            return {"playlist_id": self.playlist_id, "title": self.title, "tracks": self.tracks, "url": self.url}

        def __repr__(self):
            return str(self.__dict__())

        def download_all(self, album_title=""):
            if album_title != "":
                self.title = album_title





    @staticmethod
    def get_playlist_info(playlist_url: str):
        print(1)
        response = requests.get(playlist_url)
        print(2)
        if response.status_code != 200:
            return

        json_info = re.search(r"(?<=var ytInitialData = ).*?(?=;<\/script>)", response.text).group()
        json_info = json.loads(json_info)
        json_info = json_info["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]
        playlist_id = json_info["playlistId"]

        tracks = []
        print(2.5)
        for video in json_info["contents"]:
            video = video["playlistVideoRenderer"]

            video_title = video["title"]["runs"][0]["text"]
            video_id = video["videoId"]
            # Get the last thumbnail src. Last = better quality.
            video_thumbnail = video["thumbnail"]["thumbnails"][-1]["url"]

            tracks.append(YouTube.Track(video_id=video_id, title=video_title, thumbnail=video_thumbnail))

        print(3)
        response = requests.get(tracks[0].url)
        print(4)
        try:
            album_name = re.search(r"(?<=\"metadataRowRenderer\":{\"title\":{\"simpleText\":\".lbum\"},\"contents\":\[{\"simpleText\":\").*?(?=\"}])", response.text).group()
        except:
            album_name = input("[x]Nome do album não encontrado. Digite manualmente: ")

        album = YouTube.Album(playlist_id, album_name, tracks)

        print("[+]Álbum: "+album.title)
        print("[+]Número de músicas:", len(album.tracks))

        album.tracks[0].download(album.title)



YouTube.get_playlist_info("https://www.youtube.com/playlist?list=PLGeJR8ZOrTZdMuBWM9IYta6IoHKku0nH4")