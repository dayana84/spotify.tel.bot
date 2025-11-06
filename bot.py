import os
import time
import json
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
SUBSCRIBERS_FILE = "subscribers.json"

def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        return json.load(f)

def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subs, f)

def add_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id not in subs:
        subs.append(chat_id)
        save_subscribers(subs)
        return True
    return False

def remove_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        return True
    return False

def broadcast(bot, text):
    subs = load_subscribers()
    for chat_id in subs:
        try:
            bot.send_message(chat_id=chat_id, text=text)
        except:
            pass

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private"
))

def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! برای عضویت /subscribe و برای لغو /unsubscribe بزن.")

def subscribe(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if add_subscriber(chat_id):
        update.message.reply_text("✅ شما عضو شدید")
    else:
        update.message.reply_text("شما قبلاً عضو شده‌اید.")

def unsubscribe(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if remove_subscriber(chat_id):
        update.message.reply_text("🚫 اشتراک لغو شد")
    else:
        update.message.reply_text("شما عضو نبودید.")

def monitor_playlist(bot):
    old_tracks = [item['track']['id'] for item in sp.playlist_items(SPOTIFY_PLAYLIST_ID)['items']]
    while True:
        time.sleep(CHECK_INTERVAL)
        items = sp.playlist_items(SPOTIFY_PLAYLIST_ID)['items']
        new_tracks = [item['track']['id'] for item in items]
        added = set(new_tracks) - set(old_tracks)
        if added:
            for track_id in added:
                track = sp.track(track_id)
                name = track['name']
                artist = track['artists'][0]['name']
                url = track['external_urls']['spotify']
                message = f"🎶 آهنگ جدید:\n{name} – {artist}\n{url}"
                broadcast(bot, message)
            old_tracks = new_tracks

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe))
    threading.Thread(target=monitor_playlist, args=(updater.bot,), daemon=True).start()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
