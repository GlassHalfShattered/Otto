import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import math
import random
from main import GUILD_ID
import time
from datetime import datetime
import csv
import io
import datetime

class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.level_path = "./config/db/level.db"
        self.polymarket_path = "./config/db/polymarket.db"
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')
    @app_commands.command(name="export_level_stats", description="Download a CSV file of server level data")      
    async def export_level_stats(self, interaction: discord.Interaction):
            current_month = datetime.datetime.now().strftime('%Y-%m')
    
            try:
                with sqlite3.connect(self.level_path) as level_connection:
                        level_cursor = level_connection.cursor()
                        level_cursor.execute(
                            "SELECT User_id, Level, Xp, Level_Up_Xp, Username, Number_Of_Messages FROM Users WHERE Guild_id = ? ORDER BY Level DESC, Xp DESC",
                            (interaction.guild_id,)
                        )
                        results = level_cursor.fetchall()
                        fieldnames=["User_id", "Level", "Xp", "Level_Up_Xp", "Username", "Number_Of_Messages"]
                        data = [dict(zip(fieldnames, row)) for row in results]


                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=["User_id", "Level", "Xp", "Level_Up_Xp", "Username", "Number_Of_Messages"])
                
                writer.writeheader()
                writer.writerows(data)

                output.seek(0)
                csv_file = discord.File(fp=output, filename=f"{current_month}_level_data.csv")
                await interaction.response.send_message("Here’s your CSV file!", file=csv_file, ephemeral= True)
            except Exception as e:
                print(e)


    @app_commands.command(name="export_betterbuck_data", description="Download a CSV file of server betting data")      
    async def export_betterbuck_data(self, interaction: discord.Interaction):
            current_month = datetime.datetime.now().strftime('%Y-%m')
            await interaction.response.defer(ephemeral=True)
            try:
                with sqlite3.connect(self.polymarket_path) as poly_connection:
                        poly_cursor = poly_connection.cursor()
                        poly_cursor.execute(
                            "SELECT Date, Shares_Purchased, "
                            "Event, Resolve_Date, User_id, "
                            "BetterBucks_Spent, "
                            "BetterBucks_Before, "
                            "BetterBucks_After, "
                            "Question,"
                            "Answer,"
                            "Resolved,"
                            "Win FROM Transactions WHERE (strftime('%Y-%m', Date) = ? OR strftime('%Y-%m', Resolve_Date) = ?) "
                            "ORDER BY Date DESC", (current_month, current_month))
                            
                        
                        results = poly_cursor.fetchall()
                        fieldnames=["Date", "Shares_Purchased", "Event", "Resolve_Date", "User_id", "BetterBucks_Spent", "BetterBucks_Before", 
                        "BetterBucks_After", "Question", "Answer", "Resolved", "Win"]
                        data = [dict(zip(fieldnames, row)) for row in results]


                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=["Date", "Shares_Purchased", "Event", "Resolve_Date",
                 "User_id", "BetterBucks_Spent", "BetterBucks_Before", "BetterBucks_After", "Question", "Answer", "Resolved", "Win"])
                
                writer.writeheader()
                writer.writerows(data)

                output.seek(0)
                csv_file = discord.File(fp=output, filename=f"{current_month}_betting_data.csv")
                await interaction.followup.send("Here’s your CSV file!", file=csv_file, ephemeral= True)
            except Exception as e:
                print(e)

    

async def setup(bot):
    await bot.add_cog(Export(bot), guilds=[GUILD_ID])