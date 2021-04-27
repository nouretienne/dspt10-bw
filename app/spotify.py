import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import APIRouter
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

router = APIRouter()
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


def same_name_songs(name):
    results = sp.search(q='track:' + name, type='track', limit=20)
    table = []
    for i in range(len(results['tracks']['items'])):
        if results['tracks']['items'][i]['artists'][0]['name'] not in table[0]['name']:
            table.append({'name': results['tracks']['items'][i]['artists'][0]['name'],
                          'picture': results['tracks']['items'][i]['album']['images'][1]['url'],
                          'link': results['tracks']['items'][i]['external_urls']['spotify'],
                          'sample': results['tracks']['items'][i]['preview_url']})
    return table


def song_list_to_sample(song_list, artists):
    table = []
    for artist, song in zip(artists, song_list):
        results = sp.search(q='artist:' + artist + ' track:' + song, type='track', limit=1)
        for i in range(len(results['tracks']['items'])):
            table.append({'name': results['tracks']['items'][i]['name'],
                          'album': results['tracks']['items'][i]['album']['name'],
                          'artist': results['tracks']['items'][i]['artists'][0]['name'],
                          'sample': results['tracks']['items'][i]['external_urls']['spotify'],
                          'id': results['tracks']['items'][i]['id']})
    return table


@router.get('/spotify/get_artists')
async def get_artists(song_name):
    artists = song_to_artist(song_name)
    return {'artists': artists}


@router.get('/spotify/get_artist_sample')
async def get_sample(song_name, artists):
    spotify_dict = song_list_to_sample(song_name, artists)
    return spotify_dict


@router.get('/spotify/test_dict')
async def test_dict(song_list, artists):
    table = []
    results = sp.search(q='artist:' + artists + ' track:' + song_list, type='track', limit=1)
    table.append({'name': results['tracks']['items'][0]['name'],
                  'album': results['tracks']['items'][0]['album']['name'],
                  'artist': results['tracks']['items'][0]['artists'][0]['name'],
                  'sample': results['tracks']['items'][0]['external_urls']['spotify']})
    return table
