import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = discord.Object(os.getenv('GUILD_ID'))
intents = discord.Intents.default()
intents.message_content = True

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        # This runs after the bot connects but before on_ready
        await self.tree.sync(guild=GUILD_ID)
        print(f"Commands synced to guild {GUILD_ID.id}")

    async def on_ready(self):
        print(f'Logged on as {self.user}')

client = Client()

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load cog {filename[:-3]}: {e}")

async def main():
    async with client:
        await load_cogs()
        await client.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())