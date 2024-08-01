import discord
from collections import defaultdict
from discord.ext import commands
from music_commands import setup_music_commands

token = ''

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

voice_clients = {}
song_queue = defaultdict(list)
song_title_list = defaultdict(list)

setup_music_commands(client, voice_clients, song_queue, song_title_list)


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    await client.change_presence(status=discord.Status.idle)


client.run(token)
