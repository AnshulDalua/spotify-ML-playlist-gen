# export SPOTIPY_CLIENT_ID=aeadceb5b57e4862a060b3acc6fcecc1
# export SPOTIPY_CLIENT_SECRET=182cf6cb7d6c41c49ffa55d89ceb702f
# export SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080/ 

from ml_predictor import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
import random

def get_songs_features(ids):

    meta = spotifyObject.track(ids)
    features = spotifyObject.audio_features(ids)

    # meta
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    release_date = meta['album']['release_date']
    length = meta['duration_ms']
    popularity = meta['popularity']
    ids =  meta['id']

    # features
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    valence = features[0]['valence']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    tempo = features[0]['tempo']
    key = features[0]['key']
    time_signature = features[0]['time_signature']

    track = [name, album, artist, ids, release_date, popularity, length, danceability, acousticness,
            energy, instrumentalness, liveness, valence, loudness, speechiness, tempo, key, time_signature]
    columns = ['name','album','artist','id','release_date','popularity','length','danceability','acousticness','energy','instrumentalness',
                'liveness','valence','loudness','speechiness','tempo','key','time_signature']
    return track,columns

scope = 'playlist-modify-public'
username = 'toxicano100'

token = SpotifyOAuth(scope=scope, username=username)
spotifyObject = spotipy.Spotify(auth_manager = token)

#SPOTIPY_CLIENT_ID= 'aeadceb5b57e4862a060b3acc6fcecc1'
#SPOTIPY_CLIENT_SECRET= '182cf6cb7d6c41c49ffa55d89ceb702f'
#SPOTIPY_REDIRECT_URI= 'http://127.0.0.1:8080/' 

u#til.prompt_for_user_token(username,scope,client_id=SPOTIPY_CLIENT_ID,client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI)

#client_credentials_manager = SpotifyClientCredentials()
#spotifyObject = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

print("Welcome to playlist generator curated by your selected artists and playlist mood. ")
print("Type quit in artist dialogue when done selecting artists. ")
user_input = input('Enter artist 1 name: ')
list_of_artists_uri = []
list_of_artists_name = []
artist_counter = 2
while user_input != 'quit':
    result = spotifyObject.search(q=user_input, type = 'artist')
    list_of_artists_uri.append(result['artists']['items'][0]['uri'])
    list_of_artists_name.append(result['artists']['items'][0]['name'])
    user_input = input('Enter artist {0} name: '.format(artist_counter))
    artist_counter = artist_counter + 1

print(list_of_artists_name)

list_of_albums_name = []
list_of_albums_uri = []

i = 0
while i < len(list_of_artists_uri):
    results = spotifyObject.artist_albums(list_of_artists_uri[i], album_type='album')
    albums = results['items']
    while results['next']:
        results = spotifyObject.next(results)
        albums.extend(results['items'])
    unique = set()
    for album in albums:
        name = album['name'].lower()
        uri = album['uri']
        if name not in unique:
            unique.add(name)
            list_of_albums_uri.append(uri)
    list_of_albums_name.extend(unique)
    i = i + 1
list_of_tracks_name = []
list_of_tracks_uri = []
j = 0
while j < len(list_of_albums_name):
    tracks = []
    results = spotifyObject.album_tracks(list_of_albums_uri[j])
    tracks.extend(results['items'])
    while results['next']:
        results = spotifyObject.next(results)
        tracks.extend(results['items'])
    unique = set()
    for track in tracks:
        name = track['name'].lower()
        uri = track['uri']
        if name not in unique:
            unique.add(name)
            list_of_tracks_uri.append(uri)
    list_of_tracks_name.extend(unique)
    j = j + 1

print('What type of playlist? ')
print('1. Energetic')
print('2. Calm')
print('3. Happy')
print('4. Sad')
user_mood = int(input('Enter an answer between 1-4: '))
playlist_size = int(input('Enter length of playlist: '))

if user_mood > 4:
    print('ERROR')
if user_mood < 1:
    print('ERROR')

list_of_selected_tracks_uri = []
random.shuffle(list_of_tracks_uri)
print()
print('predicting', end =". . ß.")
k = 0
num_songs = 0
while k < len(list_of_tracks_uri):
    preds = get_songs_features(list_of_tracks_uri[k])
    track_predicted_mood = predict_mood(list_of_tracks_uri[k], preds)
    if num_songs == playlist_size:
        break
    if user_mood == 1 and track_predicted_mood == 'Energetic':
        list_of_selected_tracks_uri.append(list_of_tracks_uri[k])
        num_songs =  num_songs + 1
        print('.', end =" ")
    elif user_mood == 2 and track_predicted_mood == 'Calm' :
        list_of_selected_tracks_uri.append(list_of_tracks_uri[k])
        num_songs =  num_songs + 1
        print('.', end =" ")
    elif user_mood == 3 and track_predicted_mood == 'Happy':
        list_of_selected_tracks_uri.append(list_of_tracks_uri[k])
        num_songs =  num_songs + 1
        print('.', end =" ")
    elif user_mood == 4 and track_predicted_mood == 'Sad':
        list_of_selected_tracks_uri.append(list_of_tracks_uri[k])
        num_songs =  num_songs + 1
        print('.', end =" ")
    else:
        k = k + 1
        continue
    k = k + 1

print()
print()
playlist_name = input("Enter a playlist name: ")
playlist_description = input("Enter playlist description: ")

spotifyObject.user_playlist_create(user = username, name = playlist_name, public = True, description = playlist_description)
prePlaylist = spotifyObject.user_playlists(user=username)
playlist = prePlaylist['items'][0]['id']

spotifyObject.user_playlist_add_tracks(user=username, playlist_id = playlist, tracks = list_of_selected_tracks_uri)
print("Done!")
