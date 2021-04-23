import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


def song_to_artist(name):
    results = sp.search(q='track:' + name, type='track', limit=20)
    art = []
    long = len(results["tracks"]["items"][0]["artists"][0]["name"])
    for i in range(long):
        if results["tracks"]["items"][i]["artists"][0]["name"] not in art:
            art.append(results["tracks"]["items"][i]["artists"][0]["name"])
    return art
