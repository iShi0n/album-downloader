import requests
import json
import re
import os

class SoundCloud(object):
    def __init__(self):
        self.client_id = "N2eHz8D7GtXSl6fTtcGHdSJiS74xqOUI"

    class Track(object):
        def __init__(self, title: str, genre: str, artist: str, thumbnail: str, stream_url: str):
            self.title = title
            self.genre = genre
            self.artist = artist
            self.thumbnail = thumbnail
            self.stream_url = stream_url
            self.mp3_filename = self.tille+".mp3"

            #TODO mp3_fullpath

            if "large" in self.thumbnail:
                self.thumbnail = self.thumbnail.replace("large", "t500x500")

    class Album(object):
        def __init__(self, playlist_id: str, album_title: str, permalink: str, thumbnail: str, tracks: Track):
            self.album_title = album_title
            self.playlist_id = playlist_id
            self.permalink = permalink
            self.thumbnail = thumbnail
            self.tracks = tracks

            if "large" in self.thumbnail:
                self.thumbnail = self.thumbnail.replace("large", "t500x500")


        def download(self):
            os.mkdir(self.album_title)

            for track in self.tracks:
                ...




    def get_set_info(self, set_url: str):
        """set = playlist"""

        response = requests.get(set_url)

        if response.status_code != 200:
            raise Exception(f"status code: {response.status_code}")

        try:
            playlist_id = re.search(r"(?<=soundcloud://playlists:)\d*", response.text).group()
        except:
            raise Exception("playlist_id not found")

        tracks_json = requests.get(f"https://api.soundcloud.com/playlists/{playlist_id}?client_id={self.client_id}").json()

        tracks = []

        for track in tracks_json["tracks"]:
            title = track["title"]
            genre = track["genre"]
            artist = track["user"]["username"]
            stream_url = track["stream_url"]
            thumbnail = track["artwork_url"]

            tracks.add(SoundCloud.Track(title, genre, artist, thumbnail, stream_url))

        album_id = tracks_json["id"]
        album_title = tracks_json["title"]
        album_thumbnail = tracks_json["artwork_url"]
        album_permalink = tracks_json["permalink_url"]

        album = self.Album(album_id, album_title, album_thumbnail, tracks)




soundcloud = SoundCloud()
soundcloud.get_set_info("https://soundcloud.com/lil_peep/sets/come-over-when-youre-sober-pt")