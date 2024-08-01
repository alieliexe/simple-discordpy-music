import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio
import json
from youtube_search import YoutubeSearch
import yt_dlp

client_id = ''
client_secret = ''
redirect_uri = 'http://localhost:5000/callback'


client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

yt_dl_opts = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

async def get_song(arg, ctx, song_queue, song_title_list):
    if "https://" in arg and "playlist" in arg and "spotify" in arg:
        try:
            results = sp.playlist_tracks(arg)
            for song in results['items']:
                track = song['track']
                song_title_list[ctx.guild.id].append(track['name'])
                await search_song_in_youtube(track['name'] + track['artists'][0]['name'], ctx, song_queue)
        except Exception as err:
            print(err)

    elif "https://" in arg and "spotify" in arg and "track" in arg:
        try:
            track = sp.track(arg)
            song_title_list[ctx.guild.id].append(track['name'])  
            await search_song_in_youtube(track['name'] + track['artists'][0]['name'], ctx, song_queue)
        except Exception as err:
            print(err)

    elif "https://" in arg and "list" in arg and "yout" in arg:
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(arg, download=False))
            for Song in data['entries']:
                song = Song['url']
                song_title = Song.get('title', None)
                song_title_list[ctx.guild.id].append(song_title)
                song_queue[ctx.guild.id].append(song)
        except Exception as err:
            print(err)

    elif "https://" in arg and "youtube" in arg:
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(arg, download=False))
            song = data['url']
            song_title = data.get('title', None)
            song_title_list[ctx.guild.id].append(song_title)
            song_queue[ctx.guild.id].append(song)
        except Exception as err:
            print(err)

    else:
        try:
            keywords = arg
            yt = YoutubeSearch(keywords, max_results=1).to_json()
            yt_id = str(json.loads(yt)['videos'][0]['id'])
            url = 'https://www.youtube.com/watch?v=' + yt_id
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            song_title = data.get('title', None)
            song_title_list[ctx.guild.id].append(song_title)
            song_queue[ctx.guild.id].append(song)
        except Exception as err:
            print(err)

async def search_song_in_youtube(track, ctx, song_queue):
    keywords = track
    yt = YoutubeSearch(keywords, max_results=1).to_json()
    yt_id = str(json.loads(yt)['videos'][0]['id'])
    url = 'https://www.youtube.com/watch?v=' + yt_id
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    song_queue[ctx.guild.id].append(data['url'])
