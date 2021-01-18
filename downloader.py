from sys import argv
from youtube import YouTube
from soundcloud import SoundCloud


#TODO: melhorar banner
usage = f"""usage: python3 {argv[0]} PLAYLIST [pattern]

Download albums from youtube/soundcloud and set metadata in mp3 files

positional arguments:
    playlist: youtube/soundcloud playlist url
    pattern: (optional) pattern to be removed from the track title

eg.: python3 {argv[0]} https://www.youtube.com/playlist?list=PLGeJR8ZOrTZdMuBWM9IYta6IoHKku0nH4 'bladee - '
"""

if len(argv) < 2:
    exit("error: invalid argvs\n"+usage)

album = argv[1]
remove_from_title = ""

if len(argv) == 3:
    remove_from_title = argv[2]

if "youtube.com" in album:
    YouTube.get_playlist_info(album, remove_from_title).download()
elif "soundcloud.com" in album:
    SoundCloud.get_set_info(album, remove_from_title).download()