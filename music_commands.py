import discord
import asyncio
import random
from search_song import get_song

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

async def next_song(ctx, song_queue, song_title_list, voice_clients, client):
    if len(song_queue[ctx.guild.id]) > 0:
        try:
            player = await discord.FFmpegOpusAudio.from_probe(song_queue[ctx.guild.id][0], **ffmpeg_options)
            voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(next_song(ctx, song_queue, song_title_list, voice_clients, client), client.loop))
            song_queue[ctx.guild.id].pop(0)
            await ctx.send(f"Playing now {song_title_list[ctx.guild.id][0]}")
            await client.change_presence(status=discord.Status.online)
            song_title_list[ctx.guild.id].pop(0)
        except Exception as err:
            print("Error on play")
            print(err)
    else:
        await asyncio.sleep(60 * 10)
        if voice_clients[ctx.guild.id].is_playing() == False:
            await client.change_presence(status=discord.Status.idle)
            await voice_clients[ctx.guild.id].disconnect()
            await ctx.send("IM THE STORM THAT IS LEAVING")

def setup_music_commands(client, voice_clients, song_queue, song_title_list):

    @client.command()
    async def play(ctx, *, arg):
        try:
            if ctx.author.voice and ctx.author.voice.channel:
                voice_client = await ctx.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            else:
                await ctx.send("You are not connected to a voice channel.")
                return
        except Exception as e:
            print("Error on enter:", e)

        try:            
            await get_song(arg, ctx, song_queue, song_title_list)
            player = await discord.FFmpegOpusAudio.from_probe(song_queue[ctx.guild.id][0], **ffmpeg_options)
            voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(next_song(ctx, song_queue, song_title_list, voice_clients, client), client.loop))
            song_queue[ctx.guild.id].pop(0)
            await ctx.send(f"Playing now {song_title_list[ctx.guild.id][0]}")
            await client.change_presence(status=discord.Status.online)
            song_title_list[ctx.guild.id].pop(0)
        except Exception as err:
            print(err)

    @client.command()
    async def join(ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
            await client.change_presence(status=discord.Status.idle)
        else:
            await ctx.send("You are not connected to a voice channel.")

    @client.command()
    async def check(ctx):
        await ctx.send(f"There are {len(song_queue[ctx.guild.id])} songs in the queue")
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
            await ctx.send("There are no songs in the queue")
            await client.change_presence(status=discord.Status.idle)

    @client.command()
    async def pause(ctx):
        voice_clients[ctx.guild.id].pause()
        await ctx.send("Song paused")
        await client.change_presence(status=discord.Status.online)

    @client.command()
    async def resume(ctx):
        voice_clients[ctx.guild.id].resume()
        await ctx.send("Song resumed")
        await client.change_presence(status=discord.Status.online)

    @client.command()
    async def disconnect(ctx):
        await voice_clients[ctx.guild.id].disconnect()
        await ctx.send("IM THE STORM THAT IS LEAVING")
        await client.change_presence(status=discord.Status.idle)

    @client.command()
    async def shuffle(ctx):
        seed = random.randint(1, 1000)
        random.seed(seed)
        random.shuffle(song_queue[ctx.guild.id])
        random.seed(seed)
        random.shuffle(song_title_list[ctx.guild.id])
        await ctx.send("Songs have been shuffled")

    @client.command()
    async def checkdev(ctx):
        await ctx.send(song_queue[ctx.guild.id])
        await ctx.send(song_title_list[ctx.guild.id])
        await client.change_presence(status=discord.Status.idle)

    @client.command()
    async def test(ctx):
        await ctx.send("hi")
