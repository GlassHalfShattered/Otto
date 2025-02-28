# cogs/ping.py
import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name="ping", description="shows bot latency")
    async def ping(self, interaction: discord.Interaction):
        ping_embed = discord.Embed(title='ping', description="Latency In MS", color=discord.Color.blue())
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency (ms): ", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        ping_embed.set_footer(text=f"Requested by {interaction.user.name}.", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=ping_embed)


async def setup(bot):
    await bot.add_cog(Ping(bot), guilds=[GUILD_ID])