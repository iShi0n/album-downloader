from sys import argv
from youtube import YouTube
from soundcloud import SoundCloud

if len(argv) < 2:
    exit("error: invalid argvs")

album = argv[1]
remove_from_title = ""

if len(argv) == 3:
    remove_from_title = argv[3]

if album.startswith("https://youtube"):
    YouTube.get_playlist_info(album, remove_from_title).download()
elif album.startswith("https://soundcloud"):
    SoundCloud.get_set_info(album, remove_from_title).download()