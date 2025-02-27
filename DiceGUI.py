import discord
from typing import Final
from discord.ext import commands
from discord import app_commands
import dice
from discord.ui import Button, View
import os
from dotenv import load_dotenv

load_dotenv()
dice_value = str(6)
dice_amount = str(1)
ID: Final[str] = os.getenv('CHANNEL_ID')
class DiceSize(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)



    @discord.ui.button(label='D3',style=discord.ButtonStyle.secondary)
    async def D3(self,interaction, button):
           await interaction.response.defer()
           global dice_value
           dice_value = str(3)
    @discord.ui.button(label='D4',style=discord.ButtonStyle.secondary)
    async def D4(self,interaction, button):
           await interaction.response.defer()
           global dice_value
           dice_value = str(4)
    @discord.ui.button(label='D6',style=discord.ButtonStyle.secondary)
    async def D6(self,interaction, button):
           await interaction.response.defer()
           global dice_value
           dice_value = str(6)
    @discord.ui.button(label='D8',style=discord.ButtonStyle.secondary)
    async def D8(self,interaction, button):
           await interaction.response.defer()
           global dice_value
           dice_value = str(8)
    @discord.ui.button(label='D10',style=discord.ButtonStyle.secondary)
    async def D10(self,interaction, button):
           await interaction.response.defer()
           global dice_value
           dice_value = str(10)
    @discord.ui.button(label='D12',style=discord.ButtonStyle.secondary)
    async def D12(self,interaction, button):
           await interaction.response.defer()
           global dice_value
           dice_value = str(12)
    @discord.ui.button(label='D20',style=discord.ButtonStyle.secondary)
    async def D20(self,interaction, button):
           await interaction.response.defer()
           global dice_value
           dice_value = str(20)
    async def on_message(self, message):
        print(f'Message From {message.author}: {message.content}')
        

class DiceAmount(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='x1',style=discord.ButtonStyle.secondary)
    async def x1(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(1)
    @discord.ui.button(label='x2',style=discord.ButtonStyle.secondary)
    async def x2(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(2)

    @discord.ui.button(label='x3',style=discord.ButtonStyle.secondary)
    async def x3(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(3)

    @discord.ui.button(label='x4',style=discord.ButtonStyle.secondary)
    async def x4(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(4)

    @discord.ui.button(label='x5',style=discord.ButtonStyle.secondary)
    async def x5(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(5)

    @discord.ui.button(label='x6',style=discord.ButtonStyle.secondary)
    async def x6(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(6)

    @discord.ui.button(label='x7',style=discord.ButtonStyle.secondary)
    async def x7(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(7)

    @discord.ui.button(label='x8',style=discord.ButtonStyle.secondary)
    async def x8(self, interaction, button):
            await interaction.response.defer()
            global dice_amount
            dice_amount = str(8)

    @discord.ui.button(label='roll',style=discord.ButtonStyle.green)
    async def roll(self,interaction, button):

        
        global dice_amount
        global dice_value 
        roll = dice_amount+'d'+dice_value
        result = dice.roll(roll)
        await interaction.response.send_message(result, delete_after=10)
        channel= await interaction.guild.fetch_channel(ID)
        await channel.send(result)

    async def on_message(self, message):
        print(f'Message From {message.author}: {message.content}')

