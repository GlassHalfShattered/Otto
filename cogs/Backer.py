import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID
from cogs.GGNoms import is_in_current_week
from cogs.GGNoms import Nomination
from datetime import date, datetime

db_path = "./config/db/groove_grove.db"

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = self.get_dropdown_options()
        super().__init__(placeholder="Choose an option...", options=options)
        

    def get_dropdown_options(self):
        try:
            with sqlite3.connect(db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Username, Nomination, Date FROM Nominations")
                rows = cursor.fetchall()
            return [
                discord.SelectOption(label=row[0], value=row[0], description=row[1])
                for row in rows if is_in_current_week(row[2])
            ]
        except Exception as e:
            print(f"error: {e}")
            return []

    async def callback(self, interaction: discord.Interaction):
        
        try:
            with sqlite3.connect(db_path) as connection:
                cursor = connection.cursor()
                user = interaction.user.name
                cursor.execute("SELECT Nomination, Artist, Link FROM Nominations WHERE Username = ?", (self.values[0],))
                rows = cursor.fetchone()
                nomination = rows[0]
                artist = rows[1]
                link = rows[2]
                self.date = date.today()

                cursor.execute("UPDATE Nominations SET Nomination = ?, Artist = ?, Date = ?, Link = ? WHERE Username = ?",
                (nomination, artist, self.date, link, user))
                connection.commit()
                await interaction.response.send_message(f"{user} backed {self.values[0]} with {nomination}")
                

        except Exception as e:
            print(f"error: {e}")
            return []
    
class DropdownView(discord.ui.View):
    def __init__(self):

        super().__init__()
        self.add_item(Dropdown())

class Backer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')


    @app_commands.command(name="backer", description="buh")
    async def backer(self, interaction: discord.Interaction):
        view = DropdownView()
        await interaction.response.send_message("Please select an option:", view=view)
    




async def setup(bot):
    await bot.add_cog(Backer(bot), guilds=[GUILD_ID])