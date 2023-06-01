from bs4 import BeautifulSoup
import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# scraping billboard website for the input date
date = input("what year you would like to travel to in YYYY-MM-DD format: ")
billboard_url = "https://www.billboard.com/charts/hot-100/"
page = requests.get(f"{billboard_url}{date}")
soup = BeautifulSoup(page.text, "html.parser")
songs_100 = [song.getText().strip()
             for song in soup.select(selector="li h3")][:100]

# OAuth authenticating spotify using spotipy module
client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_sec")
redirect_url = os.environ.get("redirect")
scope = "playlist-modify-private"
auth = SpotifyOAuth(client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_url,
                    show_dialog=True,
                    cache_path="token.txt",
                    scope=scope)
sp = spotipy.Spotify(auth_manager=auth)

# Getting song URIs using search() for creating playlist
song_uris = []
year = date.split('-')[0]
for song in songs_100:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating playlist
user_id = sp.current_user()["id"]
new_playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard 100",
    description=f"These are top 100 song tracks of {date}",
    public=False)
playlist_id = new_playlist['id']

# Adding songs to play list using URIs
sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)
