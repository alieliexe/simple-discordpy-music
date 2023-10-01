import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
from youtube_search import YoutubeSearch
import json



token = "#enter your token here"
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())



voice_clients={}
song_queue = []
song_title_list = []
playlist_url = []


yt_dl_opts ={
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

ffmpeg_options =  {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }


async def after_play(ctx):
    if len(song_queue) > 0:
        try:
        
            player = await discord.FFmpegOpusAudio.from_probe(song_queue[0], **ffmpeg_options)
            voice_clients[ctx.guild.id].play(player, after = lambda e : asyncio.run_coroutine_threadsafe(after_play(ctx), client.loop))
            song_queue.pop(0)
            await ctx.send(f"Playing now {song_title_list[0]}")

            await client.change_presence(status=discord.Status.idle)            

            song_title_list.pop(0)
            

        except Exception as err:
            print("error on play")
            print(err)



@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    """
    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)}") 
    except Exception as err:
        print(err)
    """
    



@client.command()
async def play(ctx, *, arg):
    
    try:
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    
    except:
        print("erorr on enter")

    try:
        if "https://" in arg:
            try:
                url = arg
                print("go this")

            except:
                print("test")
                pass

        else:
            try:
                keywords = arg
                print(keywords)
                yt = YoutubeSearch(keywords, max_results=1).to_json()
                yt_id = str(json.loads(yt)['videos'][0]['id'])
                url = 'https://www.youtube.com/watch?v='+yt_id
                print("not this")
            except:
                pass
    
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        song = data['url']
        song_title = data.get('title', None)
        
        #i hate this ad
        if "coba hitung jumlah nya ada berapa" in song_title:
            song_queue.pop(0)
            song_title_list.pop(0)


        song_title_list.append(song_title)
        song_queue.append(song)
        player = await discord.FFmpegOpusAudio.from_probe(song_queue[0], **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after = lambda e : asyncio.run_coroutine_threadsafe(after_play(ctx), client.loop))
        song_queue.pop(0)

        await ctx.send(f"Playing now {song_title_list[0]}")
        await client.change_presence(status=discord.Status.idle)
        song_title_list.pop(0)

    except Exception as err:
        print(err)
        print("a song is already playing")

@client.command()
async def join(ctx):
    voice_client = await ctx.author.voice.channel.connect()
    voice_clients[voice_client.guild.id] = voice_client
    await client.change_presence(status=discord.Status.idle)

@client.command()
async def check(ctx):
    await ctx.send(f"There is, {len(song_queue)} song in queue")
    await client.change_presence(status=discord.Status.idle)
    for i in song_title_list:
        await ctx.send(i)

@client.command()
async def clear(ctx):
    song_queue.clear()
    song_title_list.clear()
    await ctx.send("Cleared the queue")
    await client.change_presence(status=discord.Status.idle)


@client.command()
async def skip(ctx):
    await client.change_presence(status=discord.Status.idle)
    voice_clients[ctx.guild.id].stop()
    if len(song_queue) > 0:
        await play(ctx)
        await ctx.send("Skipped current song")
    else:
        await ctx.send("There are no song in queue")

@client.command()
async def pause(ctx):
    await client.change_presence(status=discord.Status.idle)
    voice_clients[ctx.guild.id].pause()
    await ctx.send("Song paused")

@client.command()
async def resume(ctx):
    await client.change_presence(status=discord.Status.idle)
    voice_clients[ctx.guild.id].resume()
    await ctx.send("Song resumed")

@client.command()
async def disconnect(ctx):
    await client.change_presence(status=discord.Status.idle)
    await voice_clients[ctx.guild.id].disconnect()
    await ctx.send("Goodbye cyka")



@client.command()
async def hi(ctx):
    await ctx.send("hi")


@client.command()
async def test(ctx):
    await ctx.send("hi")

client.run(token)




