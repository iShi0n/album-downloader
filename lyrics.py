from __future__ import annotations
import json
import re

import requests


class Genius:
    def __init__(self) -> None:
        pass

    # (?<=\.parse\(\').*}}}}(?='\);) REGEX PEGA JSON COM LETRA
    # dar replace('\\', '')
    # dar json.dumps
    # dar json.loads
    # lyricsdata

    def search(self, name: str):
        ...
