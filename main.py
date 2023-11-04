import discord
import asyncio
import yt_dlp
import json
import random
from youtube_search import YoutubeSearch
from collections import defaultdict
from discord.ext import commands
from discord import app_commands



token = "enter token here"
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())



voice_clients={}
song_queue = defaultdict(list)
song_title_list = defaultdict(list)



yt_dl_opts ={
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

ffmpeg_options =  {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }


async def after_play(ctx):
    if len(song_queue) > 0:
        try:
        
            player = await discord.FFmpegOpusAudio.from_probe(song_queue[ctx.guild.id][0], **ffmpeg_options)
            voice_clients[ctx.guild.id].play(player, after = lambda e : asyncio.run_coroutine_threadsafe(after_play(ctx), client.loop))
            song_queue[ctx.guild.id].pop(0)
            await ctx.send(f"Playing now {song_title_list[ctx.guild.id][0]}")

            await client.change_presence(status=discord.Status.online)            

            song_title_list[ctx.guild.id].pop(0)
            

        except Exception as err:
            print("error on play")
            print(err)

    else:
        await client.change_presence(status= discord.Status.idle)





@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    await client.change_presence(status=discord.Status.idle)




@client.command()
async def play(ctx, *, arg):
    
    try:
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except:
        print("erorr on enter")

    try:
        if "https://" in arg and not "playlist" in arg:
            try:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(arg, download=False))

                song = data['url']
                song_title = data.get('title', None)

                song_title_list[ctx.guild.id].append(song_title)
                song_queue[ctx.guild.id].append(song)

            except:
                pass
        
        elif "https://" and "playlist" in arg:
            try:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(arg, download=False))

                print(data['entries'])

                for Song in data['entries']:
                    
                    song = Song['url']
                    song_title = Song.get('title', None)

                    song_title_list[ctx.guild.id].append(song_title)
                    song_queue[ctx.guild.id].append(song)

            except Exception as err:
                print(err)
                
        


        else:
            try:
                keywords = arg
                print(keywords)
                yt = YoutubeSearch(keywords, max_results=1).to_json()
                yt_id = str(json.loads(yt)['videos'][0]['id'])
                url = 'https://www.youtube.com/watch?v='+yt_id
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                song = data['url']
                song_title = data.get('title', None)

                song_title_list[ctx.guild.id].append(song_title)
                song_queue[ctx.guild.id].append(song)

            except:
                pass
    
        player = await discord.FFmpegOpusAudio.from_probe(song_queue[ctx.guild.id][0], **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after = lambda e : asyncio.run_coroutine_threadsafe(after_play(ctx), client.loop))
        song_queue[ctx.guild.id].pop(0)

        await ctx.send(f"Playing now {song_title_list[ctx.guild.id][0]}")
        await client.change_presence(status=discord.Status.online)
        song_title_list[ctx.guild.id].pop(0)

    except Exception as err:
        print(err)

@client.command()
async def join(ctx):
    voice_client = await ctx.author.voice.channel.connect()
    voice_clients[voice_client.guild.id] = voice_client
    await client.change_presence(status=discord.Status.idle)

@client.command()
async def check(ctx):
    await ctx.send(f"There is, {len(song_queue[ctx.guild.id])} song in queue")
    await client.change_presence(status=discord.Status.online)
    await ctx.send('\n'.join(song_title_list[ctx.guild.id]))


@client.command()
async def clear(ctx):
    song_queue[ctx.guild.id].clear()
    song_title_list[ctx.guild.id].clear()
    await ctx.send("Cleared the queue")
    await client.change_presence(status=discord.Status.idle)


@client.command()
async def skip(ctx):
    voice_clients[ctx.guild.id].stop()
    if len(song_queue[ctx.guild.id]) > 0:
        await play(ctx)
        await ctx.send("Skipped current song")
        await client.change_presence(status=discord.Status.online)
    else:
        await ctx.send("There are no song in queue")
        await client.change_presence(status=discord.Status.idle)


@client.command()
async def pause(ctx):
    await client.change_presence(status=discord.Status.online)
    voice_clients[ctx.guild.id].pause()
    await ctx.send("Song paused")

@client.command()
async def resume(ctx):
    await client.change_presence(status=discord.Status.online)
    voice_clients[ctx.guild.id].resume()
    await ctx.send("Song resumed")

@client.command()
async def disconnect(ctx):
    await client.change_presence(status=discord.Status.idle)
    await voice_clients[ctx.guild.id].disconnect()
    await ctx.send("IM THE STORM THAT IS LEAVING")

@client.command()
async def shuffle(ctx):

    seed = random.randint(1, 1000)
    random.seed(seed)
    random.shuffle(song_queue[ctx.guild.id])

    random.seed(seed)
    random.shuffle(song_title_list[ctx.guild.id])
    await ctx.send("Song has been shuffled")

@client.command()
async def checkdev(ctx):
    await ctx.send(song_queue[ctx.guild.id])
    await client.change_presence(status=discord.Status.idle)
    await ctx.send(song_title_list[ctx.guild.id])


@client.command()
async def test(ctx):
    await ctx.send("hi")

client.run(token)