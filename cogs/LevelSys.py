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
        self.level_path = "./config/db/level.db"
        self.polymarket_path = "./config/db/polymarket.db"

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
                try:
                    with sqlite3.connect(self.level_path) as level_connection:
                        level_cursor = level_connection.cursor()
                        level_cursor.execute("SELECT Number_Of_Messages FROM Users WHERE Guild_id = ? AND User_id = ?",
                                             (guild_id, user_id))
                        result = level_cursor.fetchone()
                        number_of_messages = result[0] + 1
                        level_cursor.execute(
                            "UPDATE Users SET Number_Of_Messages = ? WHERE Guild_id = ? AND User_id = ?",
                            (number_of_messages, guild_id, user_id))
                        level_connection.commit()
                    return
                except Exception as e:
                    print(e)
        user_cooldowns[user_id] = current_time

        try:
            with sqlite3.connect(self.level_path) as level_connection:
                level_cursor = level_connection.cursor()
                level_cursor.execute("SELECT * FROM Users WHERE Guild_id = ? AND User_id = ?", (guild_id, user_id))
                result = level_cursor.fetchone()

                if result is None:
                    cur_level = 0
                    xp = random.randint(10, 20)
                    level_up_Xp = 100
                    username = message.author.name
                    number_of_messages = 1
                    level_cursor.execute(
                        "INSERT INTO Users (Guild_id, User_id, Level, Xp, Level_Up_XP, Username, Number_Of_Messages) Values (?,?,?,?,?,?,?)",
                        (guild_id, user_id, cur_level, xp, level_up_Xp, username, number_of_messages))
                else:
                    cur_level = result[2]
                    xp = result[3] + random.randint(10, 20)
                    level_up_xp = result[4]
                    number_of_messages = result[6] + 1
                    level_cursor.execute(
                        "UPDATE Users SET Level = ?, Xp = ?, Level_Up_XP = ?, Number_Of_Messages = ?  WHERE Guild_id = ? AND User_Id = ?",
                        (cur_level, xp, level_up_xp, number_of_messages, guild_id, user_id))
                    if xp >= level_up_xp:
                        cur_level += 1
                        level_up_xp = math.ceil(50 * cur_level ** 2 + 100 * cur_level + 50)
                        await message.channel.send(f"{message.author.mention} has leveled up to level {cur_level}!")

                        level_cursor.execute(
                            "UPDATE Users SET Level = ?, Xp = ?, Level_Up_XP = ? WHERE Guild_id = ? AND User_Id = ?",
                            (cur_level, xp, level_up_xp, guild_id, user_id))
                level_connection.commit()

        except Exception as e:
            print(f"Database error: {e}")
        try:
            with sqlite3.connect(self.polymarket_path) as poly_connection:
                poly_cursor = poly_connection.cursor()
                poly_cursor.execute("SELECT BetterBucks FROM Users WHERE Guild_id = ? AND User_id = ?",
                                    (guild_id, user_id))
                result = poly_cursor.fetchone()

                if result is None:
                    bucks = float(1000)
                    username = message.author.name
                    poly_cursor.execute(
                        "INSERT INTO Users (Guild_id, User_id, BetterBucks, User_Name) Values (?,?,?,?)",
                        (guild_id, user_id, bucks, username))
                else:
                    bucks = float(result[0]) + random.randint(10, 20)
                    poly_cursor.execute("UPDATE Users SET BetterBucks = ? WHERE Guild_id = ? AND User_Id = ?",
                                        (bucks, guild_id, user_id))
                poly_connection.commit()

        except Exception as e:
            print(f"polymarket error: {e}")

    @app_commands.command(name="stats")
    async def stats(self, interaction: discord.Interaction):
        member_id = interaction.user.id
        guild_id = interaction.guild.id
        try:
            with sqlite3.connect(self.level_path) as level_connection:
                level_cursor = level_connection.cursor()
                level_cursor.execute("SELECT * FROM Users WHERE Guild_id = ? AND User_id = ?", (guild_id, member_id))
                level_result = level_cursor.fetchone()
            with sqlite3.connect(self.polymarket_path) as poly_connection:
                poly_cursor = poly_connection.cursor()
                poly_cursor.execute("SELECT BetterBucks FROM Users WHERE Guild_id = ? AND User_id = ?",
                                    (guild_id, member_id))
                user_poly_result = poly_cursor.fetchone()
            with sqlite3.connect(self.polymarket_path) as poly_connection:
                poly_cursor = poly_connection.cursor()
                poly_cursor.execute(
                    "SELECT Question, Shares_Purchased, Resolve_Date FROM Transactions WHERE User_id = ? AND Resolved = 'NO'",
                    (member_id,))
                trans_poly_result = poly_cursor.fetchall()
                trans_poly_result.sort(key=lambda x: x[2] if x[2] and 'T' in x[2] else '9999-12-31')
            level = level_result[2]
            xp = level_result[3]
            level_up_xp = level_result[4]
            number_of_messages = level_result[6]
            curr_bb = user_poly_result[0]

            stats_embed = discord.Embed(title='stats', description="User's stats", color=discord.Color.blue())
            stats_embed.add_field(name=f"{interaction.user.name}'s total XP: ", value=f"{xp}", inline=True)
            stats_embed.add_field(name=f"{interaction.user.name}'s level: ", value=f"{level}", inline=True)
            stats_embed.add_field(name=f"{interaction.user.name}'s next level up: ", value=f"{level_up_xp}",
                                  inline=True)
            stats_embed.add_field(name=f"{interaction.user.name}'total message count: ", value=f"{number_of_messages}",
                                  inline=True)
            stats_embed.add_field(name=f"{interaction.user.name}'BetterBuck Balance: ", value=f"${curr_bb}",
                                  inline=True)

            if not trans_poly_result:
                bets_text = "No upcoming bets."
            else:
                bets = []
                total_length = 0
                separator = "\n\n"
                max_length = 900 - len(" (...and more)")
                for question, shares, date in trans_poly_result:
                    if date and 'T' in date:
                        resolve_date = date.split('T')[0]
                    else:
                        resolve_date = date or "N/A"
                    bet = f'{question} - {round(shares, 2)} Resolves: {resolve_date}'
                    bet_length = len(bet)
                    if bets:
                        next_length = total_length + len(separator)
                    else:
                        next_length = bet_length

                    if next_length < max_length:
                        bets.append(bet)
                        total_length = next_length if not bets[1:] else total_length + len(separator) + bet_length
                    else:
                        break
            bets_text = separator.join(bets)
            if len(trans_poly_result) > len(bets):
                bets_text += " (...and more)"

            stats_embed.add_field(name=f"{interaction.user.name}'Upcoming Bets: ", value=f"{bets_text}", inline=False)

            stats_embed.set_footer(text=f"Requested by {interaction.user.name}.",
                                   icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
            await interaction.response.send_message(embed=stats_embed)
        except Exception as e:
            print(f'Error with stats command{e}')

    @app_commands.command(name="leaderboard", description="Displays the top levelers in the server")
    async def leaderboard(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        try:
            with sqlite3.connect(self.level_path) as level_connection:
                level_cursor = level_connection.cursor()
                level_cursor.execute(
                    "SELECT User_id, Level, Xp FROM Users WHERE Guild_id = ? ORDER BY Level DESC, Xp DESC",
                    (guild_id,)
                )
                results = level_cursor.fetchall()

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

        level_connection.commit()

    @app_commands.command(name="pointdiffs", description="Displays the closest point differences between users in the server")
    async def pointdiffs(self, interaction: discord.Interaction):
            guild_id = interaction.guild.id

            try:
                with sqlite3.connect(self.level_path) as level_connection:
                    level_cursor = level_connection.cursor()
                    level_cursor.execute(
                        "SELECT User_id, Level, Xp FROM Users WHERE Guild_id = ? ORDER BY Level DESC, Xp DESC",
                        (guild_id,)
                    )
                    results = level_cursor.fetchall()

                if not results or len(results) < 2:
                    await interaction.response.send_message("Not enough users to calculate point differences!")
                    return

                # Calculate point differences
                point_differences = []
                for i in range(len(results)):
                    for j in range(i + 1, len(results)):
                        user1_total = results[i][1] * 1000 + results[i][2]  # Level * 1000 + XP
                        user2_total = results[j][1] * 1000 + results[j][2]

                        diff = abs(user1_total - user2_total)

                        # Store difference with user information
                        point_differences.append({
                            'diff': diff,
                            'lower_user_id': results[j][0] if user1_total > user2_total else results[i][0],
                            'higher_user_id': results[i][0] if user1_total > user2_total else results[j][0],
                            'lower_total': min(user1_total, user2_total),
                            'higher_total': max(user1_total, user2_total)
                        })

                # Sort differences from smallest to largest
                point_differences.sort(key=lambda x: x['diff'])

                # Prepare the embed
                embed = discord.Embed(title="Point Differences Leaderboard", color=discord.Color.blue())

                # Fetch usernames
                usernames = {}
                for entry in point_differences[:10]:
                    for user_id in [entry['lower_user_id'], entry['higher_user_id']]:
                        if user_id not in usernames:
                            try:
                                user = await interaction.guild.fetch_member(int(user_id))
                                usernames[user_id] = user.display_name
                            except:
                                usernames[user_id] = f"Unknown User ({user_id})"

                # Add point difference descriptions
                description = []
                for i, entry in enumerate(point_differences[:10], 1):
                    lower_user = usernames.get(entry['lower_user_id'], 'Unknown')
                    higher_user = usernames.get(entry['higher_user_id'], 'Unknown')
                    description.append(
                        f"{i}) {lower_user} is {entry['diff']} points from taking over {higher_user}"
                    )

                embed.description = "\n".join(description)

                # Create the view (optional, you can modify or remove if not needed)
                view = LeaderboardView(results, interaction.guild)

                await interaction.response.send_message(embed=embed, view=view)

            except sqlite3.Error as e:
                print(f"Database error in pointdiffs: {e}")
                await interaction.response.send_message("An error occurred while calculating point differences.")
            except Exception as e:
                print(f"Unexpected error in pointdiffs: {e}")
                await interaction.response.send_message("Something went wrong!")

async def setup(bot):
    await bot.add_cog(LevelSys(bot), guilds=[GUILD_ID])