import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID
import sqlite3

class ViewSheet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./config/db/Exorcists.db"

    @app_commands.command(name="view_Sheet", description="Display Character Sheet")
    async def ping(self, interaction: discord.Interaction, cid: str):
        with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Exorcists WHERE Guild_id = ? AND CID = ?", (GUILD_ID,))
                result = cursor.fetchone()
        ping_embed = discord.Embed(title='Charcter Sheet', description="Latency In MS", color=discord.Color.blue())
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency (ms): ", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        ping_embed.set_footer(text=f"Requested by {interaction.user.name}.", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=ping_embed)

        


async def setup(bot):
    await bot.add_cog(ViewSheet(bot), guilds=[GUILD_ID])