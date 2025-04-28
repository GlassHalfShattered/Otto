import sqlite3
import discord
from discord.ext import commands, tasks
from discord import app_commands
from main import GUILD_ID
from datetime import date, datetime, timedelta
import pytz
import os
from dotenv import load_dotenv 
import asyncio
from collections import defaultdict
now = datetime.now(pytz.timezone('US/Eastern'))
today = now.date()
days_since_sunday = today.weekday() + 1  # Sunday is 0, so add
last_sunday = today - timedelta(days=days_since_sunday)
this_sunday = last_sunday + timedelta(days=7)

class Nomination(discord.ui.Modal, title="Nomination"):
    def __init__(self, db_path, bot, title="Nomination"):
        super().__init__(title=title)
        self.db_path=db_path
        self.bot = bot
        self.date = date.today()
        self.album=discord.ui.TextInput(label="Album", placeholder="Making Mirrors", required=True, style=discord.TextStyle.short)
        self.artist=discord.ui.TextInput(label="Artist", placeholder="Goyte", required=True, style=discord.TextStyle.short)
        self.link=discord.ui.TextInput(label="Link", placeholder="lsdsuici.de", required=True, style=discord.TextStyle.long)
        self.add_item(self.album)
        self.add_item(self.artist)
        self.add_item(self.link)
    async def on_submit(self, interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        userid = interaction.user.id
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Username FROM Nominations WHERE UserID = ?", (userid,))
                result = cursor.fetchone()
                if result is None:
                    try:
                            user = interaction.user.name
                            cursor = connection.cursor()
                            cursor.execute("INSERT INTO Nominations (Username, Nomination, Artist, Date, Link, UserID) VALUES (?,?,?,?,?,?)", 
                            (user, self.album.value, self.artist.value, self.date,  self.link.value, userid))
                            connection.commit()
                            await interaction.followup.send(f"{user} nominated {self.album.value} by {self.artist.value}")
                            await self.update_channel_topic()


                    except Exception as e:
                            print(f"Error2 {e}")
                else:
                        try:
                                cursor = connection.cursor()
                                user = interaction.user.name
                                cursor.execute("UPDATE Nominations SET Nomination = ?, Artist = ?, Date = ?, Link = ? WHERE UserID = ?",
                                (self.album.value, self.artist.value, self.date, self.link.value, userid))
                                connection.commit()
                                await interaction.followup.send(f"{user} nominated {self.album.value} by {self.artist.value}")
                                await self.update_channel_topic()

                        except Exception as e:
                            print(f"Error3 {e}")
        except Exception as e:
                print(f"Error1 {e}")    

    async def update_channel_topic(self,):
        print("Attempting topic update")
        try:
            load_dotenv()
            target_channel_id = os.getenv('GROOVE_GROVE')
            self.GUILD_ID = int(os.getenv('GUILD_ID'))
            guild = self.bot.get_guild(self.GUILD_ID)
            if guild is None:
                print("Guild not found")
                return False
            target_channel = guild.get_channel(int(target_channel_id))
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Nomination, Artist, Username FROM Nominations WHERE Date >= ? AND Date <= ?",
                (last_sunday.strftime('%Y-%m-%d'), this_sunday.strftime('%Y-%m-%d')))
                nominations = cursor.fetchall()

            nominations_dict = defaultdict(list)
            for nomination, artist, username in nominations:
                nominations_dict[(nomination, artist)].append(username)

            nomination_lines = []
            for (nomination, artist), usernames in nominations_dict.items():
                username_str = ', '.join(usernames)
                nomination_lines.append(f'{nomination} - {artist} ({username_str})')

            current_topic = target_channel.topic or ""
            base_topic = current_topic.split("NOMINATIONS:")[0].strip() if "NOMINATIONS:" in current_topic else current_topic
            new_topic = base_topic + " NOMINATIONS:\n" + '\n'.join(nomination_lines)
            
            async with asyncio.timeout(10):
                await target_channel.edit(topic=new_topic)

        except Exception as e:
            print(e)
            return False
        
class GGNoms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./config/db/groove_grove.db"
        self.update_topic_task.start()
        self.auto_spin_task.start()
    @tasks.loop(minutes=1)
    async def auto_spin_task(self):
        load_dotenv()
        target_channel_id = os.getenv('GROOVE_GROVE')
        self.GUILD_ID = int(os.getenv('GUILD_ID'))
        guild = self.bot.get_guild(self.GUILD_ID)
        if guild is None:
                print("Guild not found")
                return False
        target_channel = guild.get_channel(int(target_channel_id))
        now = datetime.now(pytz.timezone('US/Eastern'))
        if now.weekday() == 6 and now.hour == 23 and now.minute == 59:
            try:
                with sqlite3.connect(self.db_path) as connection:
                    cursor = connection.cursor()
                    cursor.execute("SELECT Nomination FROM Nominations WHERE Date >= ? AND Date <= ?",
                    (last_sunday.strftime('%Y-%m-%d'), this_sunday.strftime('%Y-%m-%d')))
                    result = cursor.fetchall()
                    nominations = [row[0] for row in result]
            except Exception as e:
                print(f"Error fetching nominations: {e}")
                return

            load_dotenv()
            target_channel_id = int(os.getenv('GROOVE_GROVE'))
            wheel_cog = self.bot.get_cog("Wheel")
            if wheel_cog is None:
                print("Wheel cog not found")
                return

            winner, gif_path, error = await wheel_cog.auto_spin(','.join(nominations))
            if error:
                print(f"Error: {error}")
                return
            
            channel = self.bot.get_channel(target_channel_id)
            if channel is None:
                print("Target channel not found")
                return

            try:
                with open(gif_path, "rb") as f:
                    file = discord.File(f, "wheel_of_names.gif")
                    cursor.execute("SELECT Link, Artist FROM Nominations WHERE Nomination = ?",(winner,))
                    result = cursor.fetchone()
                    link = result[0]
                    artist = result[1]
                    new_topic = f"Current: {winner} - {artist} NOMINATIONS:"
                    spotify_cog = self.bot.get_cog("Spotify")
                    if spotify_cog is None:
                            print("spotify cog not found")
                    await spotify_cog.add_album(link)
                    await channel.send(f"The wheel has spoken! Winner: {winner} {link}", file=file)
                    await channel.send(f"Added {winner} to Groove Grove")

                    async with asyncio.timeout(10):
                        await target_channel.edit(topic=new_topic)


            except Exception as e:
                print(f"Error sending spin result: {e}")

    @auto_spin_task.before_loop
    async def before_auto_spin_task(self):
        await self.bot.wait_until_ready()
    @tasks.loop(minutes=10)
    async def update_topic_task(self):
        nomination_modal = Nomination(self.db_path, self.bot)
        await nomination_modal.update_channel_topic()
    @update_topic_task.before_loop
    async def before_update_topic_task(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')
    

    @app_commands.command(name="nomination", description="Add nomination to otto")
    async def nomination(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Nomination(self.db_path,self.bot))

    @app_commands.command(name="reup", description="Reup nomination")
    async def reup(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            with sqlite3.connect(self.db_path) as connection:
                    cursor = connection.cursor()
                    userid = interaction.user.id
                    user = interaction.user.name

                    cursor.execute("SELECT Nomination, Artist FROM Nominations WHERE UserID = ?", (userid,))
                    result = cursor.fetchone()
                    nom = result[0]
                    artist = result[1]

            if result is None:
                 await interaction.followup.send("You don't have a current nomination. Use /nomination to set one.")
            else:
                self.date = date.today()
                cursor.execute("UPDATE Nominations SET Date = ? WHERE UserID = ?",(self.date,userid))
                connection.commit()
                nomination_modal = Nomination(self.db_path,self.bot)
                await interaction.followup.send(f"{user} reup'd {nom} by {artist}")
                await nomination_modal.update_channel_topic()




        except Exception as e:
                print(f"Error_nom: {e}") 
async def setup(bot):
    await bot.add_cog(GGNoms(bot), guilds=[GUILD_ID])