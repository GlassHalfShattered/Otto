import discord
from discord.ext import commands
import asyncio
import yt_dlp
from discord import app_commands
from main import GUILD_ID





class AudioPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.ffmpeg_options = {'options': '-vn'}
        self.yt_dlp_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dlp_options)


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    async def play_next(self, ctx):
        if self.queues.get(ctx.guild.id, []) != []:
            link = self.queues[ctx.guild.id].pop(0)
            await self.play(ctx, link)

    @app_commands.command(name='play', description="Pulls Otto into The Current Voice Channel And Starts Playing The Provided Youtube Link")
    async def play(self, interaction: discord.Interaction, link: str):
        try:
            await interaction.response.send_message("Audio Starting")
            voice_client = await interaction.user.voice.channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            print(f"Error connecting to voice channel: {e}")
            return

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options)

            self.voice_clients[interaction.guild.id].play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(interaction),
                    self.bot.loop
                )
            )
        except Exception as e:
            print(f"Error playing audio: {e}")

    @app_commands.command(name='pause', description="Pauses The Queue")
    async def pause(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Audio Paused")
            self.voice_clients[interaction.guild.id].pause()
        except Exception as e:
            print(f"Error pausing: {e}")

    @app_commands.command(name='resume', description="Resumes The Queue")
    async def resume(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Audio Resumed")
            self.voice_clients[interaction.guild.id].resume()
        except Exception as e:
            print(f"Error resuming: {e}")

    @app_commands.command(name='clear_queue', description="Clears The Queue")
    async def clear_queue(self, interaction: discord.Interaction):
        if interaction.guild.id in self.queues:
            self.queues[interaction.guild.id].clear()
            await interaction.response.send_message("Queue Cleared")
        else:
            await interaction.response.send_message("There Is No Queue To Clear")

    @app_commands.command(name='stop', description="Stops The Queue And Kicks Otto From Voice Channel")
    async def stop(self, interaction: discord.Interaction):
        try:
            self.voice_clients[interaction.guild.id].stop()
            await self.voice_clients[interaction.guild.id].disconnect()
            del self.voice_clients[interaction.guild.id]
            await interaction.response.send_message("Audio Stopped, Goodbye")
        except Exception as e:
            print(f"Error stopping: {e}")

    @app_commands.command(name='queue', description="Adds Youtube Videos To Queue")
    async def queue(self, interaction: discord.Interaction, link: str):
        if interaction.guild.id not in self.queues:
            self.queues[interaction.guild.id] = []
        self.queues[interaction.guild.id].append(link)
        await interaction.response.send_message("Added to Queue")

async def setup(bot):
    await bot.add_cog(AudioPlayer(bot), guilds=[GUILD_ID])