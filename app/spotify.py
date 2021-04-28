import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import APIRouter
from joblib import load
import pandas as pd
import numpy as np
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

router = APIRouter()
auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

features = ["duration_ms", "danceability", "energy", "key", "loudness", "mode", "speechiness",
            "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"]

full_features = ['popularity', 'duration_ms', 'explicit', 'danceability',
                 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature',
                 'release_date']

engineered_full_features = ['popularity', 'duration_ms', 'explicit', 'danceability',
                            'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                            'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature',
                            'year_release']

original_tracks = pd.read_csv('app/tracks.csv')
mMs = load('app/MinMaxScaler_model.joblib')
NN = load('app/NN_model.joblib')


def song_to_artist(name):
    results = sp.search(q='track:' + name, type='track', limit=20)
    art = []
    long = len(results["tracks"]["items"][0]["artists"][0]["name"])
    for i in range(long):
        if results["tracks"]["items"][i]["artists"][0]["name"] not in art:
            art.append(results["tracks"]["items"][i]["artists"][0]["name"])
    return art


def track_features(track_id, popularity, explicit, year_release):
    tid = "spotify:track:" + track_id
    analysis = sp.audio_features(tid)
    out = [analysis[0][x] for x in features]
    out.insert(0, popularity)
    out.insert(2, explicit)
    out.append(year_release)
    return pd.Series(list(out))


def same_name_songs(song, artist):
    results = sp.search(q='artist:' + artist + ' track:' + song, type='track', limit=1)
    table = []
    for i in range(len(results['tracks']['items'])):
        track_feat = [track_features(results['tracks']['items'][i]['id'],
                                     results['tracks']['items'][i]['popularity'],
                                     np.int64(results['tracks']['items'][i]['explicit']),
                                     pd.to_datetime(pd.Series(
                                         results['tracks']['items'][i]['album']['release_date'])).dt.year[
                                         0]).values]
        table.append({'link': results['tracks']['items'][i]['external_urls']['spotify'],
                      'picture': results['tracks']['items'][i]['album']['images'][0]['url'],
                      'name': results['tracks']['items'][i]['artists'][0]['name'],
                      'sample': results['tracks']['items'][i]['preview_url'],
                      'track_id': results['tracks']['items'][i]['id'],
                      'features': mMs.transform(np.array(track_feat))})
    return table


def suggestion(name):  # j number in the same_name_songs list
    liste_recommendationn = NN.kneighbors(name)[1][0]
    recom = []
    for i in range(10):
        recom.append({'artist': original_tracks.iloc[liste_recommendationn[i]][['artists']],
                      'link': 'https://open.spotify.com/track/' + original_tracks.iloc[liste_recommendationn[i]][['id']].values[0],
                      'id': original_tracks.iloc[liste_recommendationn[i]][['id']].values[0]})
    return recom


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
