import requests
import re
import os
import eyed3

class SoundCloud(object):
    client_id = "N2eHz8D7GtXSl6fTtcGHdSJiS74xqOUI"

    class Track(object):
        """Classe para faixas do album"""

        def __init__(self, title: str, genre: str, artist: str, thumbnail: str, stream_url: str, track: int) -> None:
            self.title = title
            self.genre = genre
            self.artist = artist
            self.thumbnail = thumbnail
            self.stream_url = stream_url+"?client_id="+SoundCloud.client_id
            self.mp3_filename = self.title+".mp3"
            self.track = track

            # TODO mp3_fullpath

            if "large" in self.thumbnail:
                self.thumbnail = self.thumbnail.replace("large", "t500x500")
            
            self.thumbnail_content = requests.get(self.thumbnail).content

        def set_metadata(self, remove_from_title=""):
            """Seta os metadados no mp3

            Args:
                remove_from_title (str, optional): remove um texto do titule da música. ex. se o titulo for bladee - romeo, você pode passar "bladee - " para a função para que seja removido. Defaults to "".
            """
            
            title = self.title.replace(remove_from_title, "")

            mp3_file = eyed3.load(self.mp3_fullpath)
        
            mp3_file.initTag()

            mp3_file.tag.title = title
            mp3_file.tag.artist = self.artist
            mp3_file.tag.album = self.album_title
            mp3_file.tag.track_num  = self.track
            mp3_file.tag.images.set(3, self.thumbnail_content, "image/jpeg", self.album_title)
            mp3_file.tag.save()

        def download(self, album_title: str):
            self.album_title = album_title
            self.mp3_fullpath = f"{album_title}/{self.mp3_filename}"

            with open(self.mp3_fullpath, "wb") as mp3_file:
                mp3_content = requests.get(self.stream_url).content
                mp3_file.write(mp3_content)
                mp3_file.close()
            
            self.set_metadata()

    class Album(object):
        def __init__(self, playlist_id: str, album_title: str, permalink: str, thumbnail: str, tracks: "Tracks") -> None:
            self.album_title = album_title
            self.playlist_id = playlist_id
            self.permalink = permalink
            self.thumbnail = thumbnail
            self.tracks = tracks

            if "large" in self.thumbnail:
                self.thumbnail = self.thumbnail.replace("large", "t500x500")

        def download(self):
            try:
                os.mkdir(self.album_title)
            except FileExistsError:
                pass
            except Exception as e:
                exit(str(e))

            with open(f"{self.album_title}/art.jpg", "wb") as art_file:
                art_content = requests.get(self.thumbnail).content
                art_file.write(art_content)
                art_file.close()
                
            for track in self.tracks:
                track.download(self.album_title)

    def get_set_info(self, set_url: str) -> "Album":
        """Pega informações do set (album/playlist).

        Raises:
            Exception: Status code != 200
            Exception: playlist_id not found

        Returns:
            Album: Objeto do album
        """

        response = requests.get(set_url)

        if response.status_code != 200:
            raise Exception(f"status code: {response.status_code}")

        try:
            playlist_id = re.search(
                r"(?<=soundcloud://playlists:)\d*", response.text).group()
        except:
            raise Exception("playlist_id not found")

        tracks_json = requests.get(
            f"https://api.soundcloud.com/playlists/{playlist_id}?client_id={self.client_id}").json()

        tracks = []

        for track_num, track in enumerate(tracks_json["tracks"]):
            title = track["title"]
            genre = track["genre"]
            artist = track["user"]["username"]
            stream_url = track["stream_url"]
            thumbnail = track["artwork_url"]

            tracks.append(SoundCloud.Track(title, genre, artist, thumbnail, stream_url, track_num+1))

        album_id = tracks_json["id"]
        album_title = tracks_json["title"]
        album_thumbnail = tracks_json["artwork_url"]
        album_permalink = tracks_json["permalink_url"]

        album = self.Album(album_id, album_title,album_permalink, album_thumbnail, tracks)

        return album
