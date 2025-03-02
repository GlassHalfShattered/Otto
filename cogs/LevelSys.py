
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import math
import random
from main import GUILD_ID
import time


user_cooldowns = {}
COOLDOWN_TIME = 120


class LeaderboardView(discord.ui.View):
    def __init__(self, leaderboard_data, guild, entries_per_page=10):
        super().__init__(timeout=60)
        self.leaderboard_data = leaderboard_data
        self.guild = guild
        self.entries_per_page = entries_per_page
        self.current_page = 0
        self.total_pages = math.ceil(len(leaderboard_data) / entries_per_page)

        
        if self.total_pages <= 1:
            self.prev_button.disabled = True
            self.next_button.disabled = True

    def build_embed(self):
        start_idx = self.current_page * self.entries_per_page
        end_idx = min(start_idx + self.entries_per_page, len(self.leaderboard_data))
        page_data = self.leaderboard_data[start_idx:end_idx]

        embed = discord.Embed(
            title=f"🏆 Level Leaderboard for {self.guild.name}",
            color=discord.Color.gold(),
            description=f"Page {self.current_page + 1} of {self.total_pages}"
        )
        embed.set_thumbnail(url=self.guild.icon.url if self.guild.icon else None)

        leaderboard_text = ""
        for i, (user_id, level, xp) in enumerate(page_data, start_idx + 1):
            member = self.guild.get_member(user_id)
            name = member.display_name if member else f"Unknown User ({user_id})"
            leaderboard_text += f"**{i}. {name}** - Level {level} (XP: {xp})\n"

        embed.add_field(name="Top Levelers", value=leaderboard_text or "No entries.", inline=False)
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            if self.current_page == 0:
                self.prev_button.disabled = True
            self.next_button.disabled = False
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            if self.current_page == self.total_pages - 1:
                self.next_button.disabled = True
            self.prev_button.disabled = False
            await interaction.response.edit_message(embed=self.build_embed(), view=self)


            
class LevelSys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./config/db/level.db"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        
        guild_id = message.guild.id
        user_id = message.author.id
        current_time = time.time()


        if user_id in user_cooldowns:
            last_triggered = user_cooldowns[user_id]
            if current_time - last_triggered < COOLDOWN_TIME:
                return
        user_cooldowns[user_id] = current_time
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Users WHERE Guild_id = ? AND User_id = ?", (guild_id, user_id))
                result = cursor.fetchone()

                if result is None:
                    cur_level = 0
                    xp = random.randint(10, 20)
                    level_up_Xp = 100
                    cursor.execute("INSERT INTO Users (Guild_id, User_id, Level, Xp, Level_Up_XP) Values (?,?,?,?,?)",(guild_id, user_id, cur_level, xp, level_up_Xp))
                else:
                    cur_level = result[2]
                    xp = result[3] + random.randint(10, 20)
                    level_up_xp = result[4]
                    cursor.execute("UPDATE Users SET Level=?, Xp = ?, Level_Up_XP = ? WHERE Guild_id = ? AND User_Id = ?", (cur_level, xp, level_up_xp, guild_id, user_id))
                    if xp >= level_up_xp:
                        cur_level += 1
                        level_up_xp = math.ceil(50 *cur_level ** 2 + 100 * cur_level + 50)
                        await message.channel.send(f"{message.author.mention} has leveled up to level {cur_level}!")
                        
                        cursor.execute("UPDATE Users SET Level=?, Xp = ?, Level_Up_XP = ? WHERE Guild_id = ? AND User_Id = ?", (cur_level, xp, level_up_xp, guild_id, user_id))
                connection.commit()        

        except Exception as e:
            print(f"Database error: {e}")

    @app_commands.command(name="level")
    async def level(self, interaction: discord.Interaction):
        member_id = interaction.user.id
        guild_id = interaction.guild.id
        with sqlite3.connect(self.db_path) as connection:

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Users WHERE Guild_id = ? AND User_id = ?", (guild_id, member_id))
            result = cursor.fetchone()

        level = result[2]
        xp = result[3]
        level_up_xp = result[4]

        level_embed = discord.Embed(title='level', description="User's level", color=discord.Color.blue())
        level_embed.add_field(name=f"{interaction.user.name}'s total XP: ", value=f"{xp}", inline=False)
        level_embed.add_field(name=f"{interaction.user.name}'s level: ", value=f"{level}", inline=False)
        level_embed.add_field(name=f"{interaction.user.name}'s next level up: ", value=f"{level_up_xp}", inline=False)
        level_embed.set_footer(text=f"Requested by {interaction.user.name}.", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=level_embed)
        connection.commit()

      
    @app_commands.command(name="leaderboard", description="Displays the top levelers in the server")
    async def leaderboard(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT User_id, Level, Xp FROM Users WHERE Guild_id = ? ORDER BY Level DESC, Xp DESC",
                    (guild_id,)
                )
                results = cursor.fetchall()

            if not results:
                await interaction.response.send_message("No one has started leveling in this server yet!")
                return

            # Create the paginated view
            view = LeaderboardView(results, interaction.guild)
            await interaction.response.send_message(embed=view.build_embed(), view=view)

        except sqlite3.Error as e:
            print(f"Database error in leaderboard: {e}")
            await interaction.response.send_message("An error occurred while fetching the leaderboard.")
        except Exception as e:
            print(f"Unexpected error in leaderboard: {e}")
            await interaction.response.send_message("Something went wrong!")
                   

        
        connection.commit()

async def setup(bot):
    await bot.add_cog(LevelSys(bot), guilds=[GUILD_ID])