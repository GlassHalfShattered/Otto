import discord
from discord.ext import commands
from discord import app_commands
import dice
from main import GUILD_ID
import os
from dotenv import load_dotenv



class dicebot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        load_dotenv()
        self.dice_value = str(6)
        self.dice_amount = str(1)
        self.ID = os.getenv('CHANNEL_ID')


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    #Calls the GUI
    @app_commands.command(name="dice_roller_gui", description="Sends The Dice Roller GUI To Channel")
    async def dicerollergui(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=DiceSize(self))
        await interaction.followup.send(view=DiceAmount(self))


    #Rolls Dice Through CLI
    @app_commands.command(name="dice_roller", description="Rolls Dice Through CLI")
    async def dice_roller(self, interaction: discord.Interaction, dice_amount:str, dice_value:str):
        roll = dice_amount+'d'+dice_value
        result = dice.roll(roll)
        await interaction.response.send_message(f'{interaction.user.name} rolled: {result}')

        
class DiceSize(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label='D3',style=discord.ButtonStyle.secondary)
    async def D3(self,interaction, button):
        await interaction.response.defer()
        self.cog.dice_value = str(3)

    @discord.ui.button(label='D4',style=discord.ButtonStyle.secondary)
    async def D4(self,interaction, button):
        await interaction.response.defer()
           
        self.cog.dice_value = str(4)

    @discord.ui.button(label='D6',style=discord.ButtonStyle.secondary)
    async def D6(self,interaction, button):
        await interaction.response.defer()
          
        self.cog.dice_value = str(6)

    @discord.ui.button(label='D8',style=discord.ButtonStyle.secondary)
    async def D8(self,interaction, button):
        await interaction.response.defer()
          
        self.cog.dice_value = str(8)

    @discord.ui.button(label='D10',style=discord.ButtonStyle.secondary)
    async def D10(self,interaction, button):
        await interaction.response.defer()
           
        self.cog.dice_value = str(10)

    @discord.ui.button(label='D12',style=discord.ButtonStyle.secondary)
    async def D12(self,interaction, button):
        await interaction.response.defer()
           
        self.cog.dice_value = str(12)

    @discord.ui.button(label='D20',style=discord.ButtonStyle.secondary)
    async def D20(self,interaction, button):
        await interaction.response.defer()
           
        self.cog.dice_value = str(20)
    

class DiceAmount(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label='x1',style=discord.ButtonStyle.secondary)
    async def x1(self, interaction, button):
        await interaction.response.defer()
        self.cog.dice_amount = str(1)

    @discord.ui.button(label='x2',style=discord.ButtonStyle.secondary)
    async def x2(self, interaction, button):
        await interaction.response.defer()

        self.cog.dice_amount = str(2)

    @discord.ui.button(label='x3',style=discord.ButtonStyle.secondary)
    async def x3(self, interaction, button):
        await interaction.response.defer()
        self.cog.dice_amount = str(3)

    @discord.ui.button(label='x4',style=discord.ButtonStyle.secondary)
    async def x4(self, interaction, button):
        await interaction.response.defer()
        self.cog.dice_amount = str(4)

    @discord.ui.button(label='x5',style=discord.ButtonStyle.secondary)
    async def x5(self, interaction, button):
        await interaction.response.defer()
        self.cog.dice_amount = str(5)

    @discord.ui.button(label='x6',style=discord.ButtonStyle.secondary)
    async def x6(self, interaction, button):
        await interaction.response.defer()
        self.cog.dice_amount = str(6)

    @discord.ui.button(label='x7',style=discord.ButtonStyle.secondary)
    async def x7(self, interaction, button):
        await interaction.response.defer()
        self.cog.dice_amount = str(7)

    @discord.ui.button(label='x8',style=discord.ButtonStyle.secondary)
    async def x8(self, interaction, button):
        await interaction.response.defer()
        self.cog.dice_amount = str(8)

    @discord.ui.button(label='roll',style=discord.ButtonStyle.green)
    async def roll(self,interaction, button):

        roll = self.cog.dice_amount+'d'+self.cog.dice_value
        result = dice.roll(roll)
        await interaction.response.send_message(result, delete_after=10)
        try:
                print(f"Attempting to fetch channel with ID: {self.cog.ID}")
                channel = await interaction.guild.fetch_channel(self.cog.ID)
                print(f"Channel fetched: {channel.name} (ID: {channel.id})")
                await channel.send(result)
                print(f"Result sent to channel: {result}")
        except discord.errors.NotFound:
                print(f"Error: Channel with ID {self.cog.ID} not found")
                await interaction.followup.send(f"Error: Archive channel not found", ephemeral=True)
        except discord.errors.Forbidden:
                print(f"Error: Bot lacks permission to send to channel {self.cog.ID}")
                await interaction.followup.send(f"Error: I don’t have permission to send to the archive channel", ephemeral=True)
        except Exception as e:
                print(f"Unexpected error sending to channel {self.cog.ID}: {e}")
                await interaction.followup.send(f"Error sending to archive: {e}", ephemeral=True)




async def setup(bot):
    await bot.add_cog(dicebot(bot), guilds=[GUILD_ID])