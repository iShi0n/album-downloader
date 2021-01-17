import os
import re
import json
import subprocess

import eyed3
import pytube  # TODO: try to make it manually
import requests


class YouTube(object):
    class Track(object):
        def __init__(self, video_id: str, thumbnail: str, title: str, track: int) -> None:
            self.video_id = video_id
            self.title = title
            self.track = track
            self.thumbnail_src = thumbnail
            #self.thumbnail = requests.get(self.thumbnail_src).content
            self.url = "https://youtube.com/watch?v="+self.video_id
            self.mp3_src = pytube.YouTube(self.url).streams.filter(only_audio=True).last().url

            self.mp3_filename = f"{self.title}.mp3"
            self.mp3_filename = re.sub(r'\\|/|:|\?|\"|\<|\>', ' ', self.mp3_filename)

        def __dict__(self):
            return {"video_id": self.video_id, "title": self.title, "thumbnail": self.thumbnail_src, "url": self.url}

        def __repr__(self):
            return str(self.__dict__())

        def download(self, album_title: str):
            #TODO: printar qual track está sendo baixada

            self.mp3_full_path = re.sub(r'\\|/|:|\?|\"|\<|\>', '', album_title)+"/"+self.mp3_filename

            with open(self.mp3_full_path, "wb") as mp3_file:
                mp3_content = requests.get(self.mp3_src).content
                mp3_file.write(mp3_content)
                mp3_file.close()

            self.convert()
            self.set_metadata(album_title, remove_from_title="bladee - ")

        def _get_artist(self) -> str:
            """Parsea a página e retorna o nome do artista.

            Returns:
                str: nome do artista
            """

            response = requests.get(self.url)

            try:
                # TODO: tentar capturar Artist e Artista. (caso esteja em outra linguagem)
                artist_name = re.search(r"(?<=\"metadataRowRenderer\":{\"title\":{\"simpleText\":\"Artista\"},\"contents\":\[{\"simpleText\":\").*?(?=\"}])", response.text).group()
            except:
                artist_name = input("[x]Nome do artista não encontrado. Digite manualmente: ")

            return artist_name

        def convert(self):
            """Converte o arquivo ara mp3 para suportar as tags."""

            subprocess.call(f'ffmpeg -i "{self.mp3_full_path}" "tmp-{self.mp3_filename}"', shell=True, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(self.mp3_full_path)
            os.rename(f'tmp-{self.mp3_filename}', self.mp3_full_path)

        def set_metadata(self, album_title, remove_from_title=""):
            """Seta os metadados do mp3

            Args:
                album_title ([type]): nome do album
                remove_from_title (str, optional): string a ser removida do titulo da música. Defaults to "".
            """

            title = self.title.replace(remove_from_title, "")

            mp3_file = eyed3.load(self.mp3_full_path)
            mp3_file.initTag()

            mp3_file.tag.title = title
            mp3_file.tag.track_num = self.track
            mp3_file.tag.artist = self._get_artist()
            mp3_file.tag.album = album_title
            mp3_file.tag.save()

    class Album(object):
        def __init__(self, playlist_id: str, title: str, tracks: "Track", thumbnail: str) -> None:
            self.playlist_id = playlist_id
            self.title = title
            self.thumbnail = thumbnail
            self.tracks = tracks
            self.url = "https://youtube.com/playlist?list="+self.playlist_id

            super().__init__()

        def __dict__(self):
            return {"playlist_id": self.playlist_id, "title": self.title, "tracks": self.tracks, "url": self.url}

        def __repr__(self):
            return str(self.__dict__())

        def download(self, album_title=""):
            if album_title != "":
                self.title = album_title

            try:
                os.mkdir(self.title)
            except FileExistsError:
                pass
            except Exception as e:
                exit(str(e))
                

            with open(f"{self.title}/art.jpg", "wb") as art_file:
                art_content = requests.get(self.thumbnail).content
                art_file.write(art_content)
                art_file.close()
                
            for track in self.tracks:
                track.download(self.title)

    @staticmethod
    def get_playlist_info(playlist_url: str, remove_from_title: str = "") -> "Album":
        """Pega todas informações do album

        Returns:
            YouTube.Album: Objeto do tipo Album
        """

        response = requests.get(playlist_url)

        if response.status_code != 200:
            return

        json_info = re.search(r"(?<=var ytInitialData = ).*?(?=;<\/script>)", response.text).group()
        json_info = json.loads(json_info)
        json_info = json_info["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]
        playlist_id = json_info["playlistId"]

        tracks = []
        album_thumbnail = ""

        for track, video in enumerate(json_info["contents"]):
            video = video["playlistVideoRenderer"]

            video_title = video["title"]["runs"][0]["text"]
            video_id = video["videoId"]
            # Get the last thumbnail src. Last = better quality.
            video_thumbnail = video["thumbnail"]["thumbnails"][-1]["url"]
            
            if track == 0:
                album_thumbnail = video_thumbnail

            tracks.append(YouTube.Track(video_id=video_id, title=video_title.replace(remove_from_title, ""), thumbnail=video_thumbnail, track=track+1))

        response = requests.get(tracks[0].url)

        try:
            album_name = re.search(r"(?<=\"metadataRowRenderer\":{\"title\":{\"simpleText\":\".lbum\"},\"contents\":\[{\"simpleText\":\").*?(?=\"}])", response.text).group()
        except:
            album_name = input("[x]Nome do album não encontrado. Digite manualmente: ")

        album = YouTube.Album(playlist_id, album_name, tracks, album_thumbnail)

        print("[+]Álbum: "+album.title)
        print("[+]Número de músicas:", len(album.tracks))

        return album
