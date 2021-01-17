from sys import argv
from youtube import YouTube
from soundcloud import SoundCloud

if len(argv) < 2:
    exit("error: invalid argvs")

album = argv[1]
remove_from_title = ""

if len(argv) == 3:
    remove_from_title = argv[2]

if "youtube.com" in album:
    YouTube.get_playlist_info(album, remove_from_title).download()
elif "soundcloud.com" in album:
    SoundCloud.get_set_info(album, remove_from_title).download()