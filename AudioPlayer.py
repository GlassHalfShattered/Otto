import discord
from discord.ext import commands
import asyncio
import yt_dlp
from main import main
from typing import Optional

queues = {}
voice_clients = {}
ffmpeg_options = {'options': '-vn'}
yt_dlp_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dlp_options)


class AudioPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    async def play_next(self, ctx):
        if queues.get(ctx.guild.id, []) != []:
            link = queues[ctx.guild.id].pop(0)
            await self.play(ctx, link)

    @commands.hybrid_command(name='play', description="Pulls Otto into The Current Voice Channel And Starts Playing The Provided Youtube Link")
    async def play(self, ctx, link: str):
        try:
            await ctx.send("Audio Starting")
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            print(f"Error connecting to voice channel: {e}")
            return

        try:
            data = await main.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

            voice_clients[ctx.guild.id].play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx),
                    self.client.loop
                )
            )
        except Exception as e:
            print(f"Error playing audio: {e}")

    @commands.hybrid_command(name='pause', description="Pauses The Queue")
    async def pause(self, ctx):
        try:
            await ctx.send("Audio Paused")
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(f"Error pausing: {e}")

    @commands.hybrid_command(name='resume', description="Resumes The Queue")
    async def resume(self, ctx):
        try:
            await ctx.send("Audio Resumed")
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(f"Error resuming: {e}")

    @commands.hybrid_command(name='clear_queue', description="Clears The Queue")
    async def clear_queue(self, ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue Cleared")
        else:
            await ctx.send("There Is No Queue To Clear")

    @commands.hybrid_command(name='stop', description="Stops The Queue And Kicks Otto From Voice Channel")
    async def stop(self, ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
            await ctx.send("Audio Stopped, Goodbye")
        except Exception as e:
            print(f"Error stopping: {e}")

    @commands.hybrid_command(name='queue', description="Adds Youtube Videos To Queue")
    async def queue(self, ctx, link: str):
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []
        queues[ctx.guild.id].append(link)
        await ctx.send("Added to Queue")

async def setup(bot):
    await bot.add_cog(AudioPlayer(bot))