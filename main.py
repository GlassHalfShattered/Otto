import discord
from typing import Final
from discord.ext import commands
import dice
import os
from dotenv import load_dotenv
from DiceGUI import DiceSize
from DiceGUI import DiceAmount
import asyncio
import yt_dlp



load_dotenv()
ID: Final[str] = os.getenv('CHANNEL_ID')
guid: Final[str] = os.getenv('GUILD_ID')
intents = discord.Intents.default()
intents.message_content = True
voice_clients = {}
yt_dlp_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dlp_options)
queues = {}
ffmpeg_options = {'options': '-vn'}
GUILD_ID = discord.Object(guid)


class Client(commands.Bot,):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    async def on_ready(self):
        print(f'Logged on as {self.user}')
      
    #async def sync(self,):
        try:
            guild = discord.Object(guid)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e:
         print(f'Error syncing commands: {e}')

 

    async def on_message(self, message):
        print(f'Message From {message.author}: {message.content}')

client = Client()
                          
async def Loadcog():
        for filename in os.listdir("./cogs"):
             if filename.endswith(".py"):
                 await client.load_extension(f"cogs.{filename[:-3]}")


async def main():
     async with client:
            await Loadcog()
            await client.start(os.getenv("DISCORD_TOKEN"))

async def play_next(ctx):
    if queues[ctx.guild.id] != []:
        link = queues[ctx.guild.id].pop(0)
    await play(ctx, link)

  
  

@client.tree.command(name='play',description="Pulls Otto into The Current Voice Channel And Starts Playing The Provided Youtube Link", guild=GUILD_ID)
async def play(ctx,link: str):
        try:
            await ctx.response.send_message("Audio Starting")
            voice_client = await ctx.user.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

  

        try:
             loop = asyncio.get_event_loop()
             data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))
             song=data['url']
             player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
             voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx),client.loop))
        except Exception as e:
            print(e)

@client.tree.command(name='pause',description = "Pauses The Queue", guild=GUILD_ID)
async def pause(ctx):

        try:
            await ctx.response.send_message("Audio Paused")
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)

@client.tree.command(name='resume',description = "Resumes The Queue", guild=GUILD_ID)

async def resume(ctx):

        try: 
            await ctx.response.send_message("Audio Resumed")
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)

  
  

@client.tree.command(name='clear_queue',description = "Clears The Queue", guild=GUILD_ID)
async def clear_queue(ctx):
    if ctx.guild.id in queues:
         queues[ctx.guild.id].clear()
         await ctx.response.send_message("Queue Cleared")
    else:
        await ctx.response.send_message("There Is No Queue To Clear")

  
  

@client.tree.command(name='stop', description = "Stops The Queue And Kicks Otto From Voice Channel", guild=GUILD_ID)
async def stop(ctx):

    try:
        voice_clients[ctx.guild.id].stop()
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
        await ctx.response.send_message("Audio Stopped, Goodbye")

  

    except Exception as e:
        print(e)

  

@client.tree.command(name="queue", description = "Adds Youtube Vidoes To Queue", guild=GUILD_ID)
async def queue(ctx, link: str):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
        queues[ctx.guild.id].append(link)
        await ctx.response.send_message("Added to Queue")







#Dice Roller CLI
@client.tree.command(name="dice_roller", description="Rolls Dice Through CLI", guild=GUILD_ID)
async def dice_roller(interaction: discord.Interaction, amount: str, size: str):
    roll = amount+'d'+size
    result = dice.roll(roll)
    await interaction.response.send_message(result, delete_after=10)
    channel= await interaction.guild.fetch_channel(ID)
    await channel.send(result)



#Editable SIN Embed
#@client.tree.command(name="ashpool", description="BBEG", guild=GUILD_ID)
#async def ashpool(interaction: discord.Interaction):
#    embed = discord.Embed(title="Ashpool", url=URL,color=discord.Color.red(), description="BBEG")
#    embed.set_thumbnail(url="")
#    await interaction.response.send_message(embed=embed)



#Help Embed
@client.tree.command(name="help", description="List Of Commands", guild=GUILD_ID)
async def Help(interaction: discord.Interaction):
    embed = discord.Embed(title="Help",color=discord.Color.red(),)
    embed.add_field(name="Music Player Commands", value="/Play, /Pause, /Resume, /Queue, /Stop. /Play and /Queue Require A Space Between The Command And The URL.")
    embed.add_field(name="Dice Roller Commands", value="/Dice_Roller Rolls Dice With Two Inputs, Dice Size and Dice Amount")
    embed.add_field(name="Dice Roller GUI", value="Dice Roller GUI Brings Up A Button GUI, Then Sends A Temporary Message To The Current Channel And A Permanent Message To #Otto-Speaks")
    embed.set_thumbnail(url="https://c7.alamy.com/comp/2GXF8CE/sign-with-the-word-help-in-a-hand-icon-in-cartoon-style-on-a-white-background-2GXF8CE.jpg")
    await interaction.response.send_message(embed=embed)






#Dice Roller GUI
@client.tree.command(name="dice_roller_gui", description="Sends The Dice Roller GUI To Channel", guild=GUILD_ID)
async def dicerollergui(interaction: discord.Interaction,):
    await interaction.response.send_message(view=DiceSize())
    await interaction.followup.send(view=DiceAmount())




asyncio.run(main())