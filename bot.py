import os
import time
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from telegram import Bot

# ======= Load Environment Variables =======
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
SPOTIFY_PLAYLIST_ID = os.environ.get("SPOTIFY_PLAYLIST_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 60))

# ======= Initialize Spotify & Telegram =======
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private"
))

bot = Bot(token=TELEGRAM_TOKEN)

# ======= Keep Track of Already Seen Tracks =======
seen_tracks = set()

# ======= Main Loop =======
while True:
    playlist = sp.playlist_items(SPOTIFY_PLAYLIST_ID)
    for item in playlist['items']:
        track_id = item['track']['id']
        track_name = item['track']['name']
        if track_id not in seen_tracks:
            seen_tracks.add(track_id)
            message = f"New track added: {track_name}"
            # Send message to Telegram (replace chat_id with your channel or chat ID)
            bot.send_message(chat_id="@YourChannelOrChatID", text=message)
    time.sleep(CHECK_INTERVAL)
