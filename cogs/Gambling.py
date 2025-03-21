import requests
import json
import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID
import sqlite3
from datetime import date


class Buy_yes(discord.ui.Modal, title="Buy Yes"):
    def __init__(self, parent_view: 'Polymarket', yes_price: str, question: str):
        super().__init__()
        self.parent_view = parent_view
        self.yes_price = yes_price 
        self.question = question
        try:
            with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT BetterBucks FROM Users WHERE User_id = ? AND Guild_id = ?",
                    (self.parent_view.member_id, self.parent_view.guild_id)
                )
                result = cursor.fetchone()
                self.curr_bb = float(result[0]) if result else "0"
                self.buy_yes = discord.ui.TextInput(
                label=f"Yes Shares are {self.yes_price} - You have ${self.curr_bb}", 
                placeholder="How much would you like to bet?",
                style=discord.TextStyle.short
            )
            self.add_item(self.buy_yes)
        except Exception as e:
            print(f"Error in Buy_yes init: {e}")

    async def on_submit(self, interaction: discord.Interaction):
        try:    
                
                bb_spent = float(self.buy_yes.value)
                new_bb = self.curr_bb - bb_spent
                if new_bb >= 0:
                    shares = bb_spent / float(self.yes_price)
                    current_date = date.today()
                    answer = 'yes'
                    with sqlite3.connect(self.parent_view.db_path) as connection:
                        cursor = connection.cursor()
                        cursor.execute("INSERT INTO transactions "
                        "(BetterBucks_Before, "
                        "BetterBucks_Spent, "
                        "Shares_Purchased, "
                        "User, "
                        "Event, "
                        "Question, "
                        "Answer, "
                        "BetterBucks_After, "
                        "Date, Resolve_Date) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (self.curr_bb,bb_spent,shares, self.parent_view.member_id,self.parent_view.event['title'],self.question, answer,new_bb,current_date, self.parent_view.end_date)
                        )
                        cursor.execute("UPDATE Users SET BetterBucks = ? WHERE User_id = ? AND Guild_id = ?",
                        (new_bb, self.parent_view.member_id, self.parent_view.guild_id))

                        connection.commit()
                        await interaction.response.send_message(f"Bet placed: ${bb_spent} on Yes at {self.yes_price}. Bet will resolve on {self.parent_view.end_date}.")
                if new_bb < 0:
                    await interaction.response.send_message("You don't have enough BetterBucks for that.", ephemeral=True)
                    
        except Exception as e:
                print(f"Error in Buy_yes on_submit: {e}")
                await interaction.response.send_message("Something went wrong. Do you have enough BetterBucks?", ephemeral=True)

class Buy_no(discord.ui.Modal, title="Buy No"):
    def __init__(self, parent_view: 'Polymarket', no_price: str, question: str):
        super().__init__()
        self.parent_view = parent_view
        self.no_price = no_price
        self.question = question
        try:
            with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT BetterBucks FROM Users WHERE User_id = ? AND Guild_id = ?",
                    (self.parent_view.member_id, self.parent_view.guild_id)
                )
                result = cursor.fetchone()
                self.curr_bb = result[0] if result else "None"
            self.buy_no = discord.ui.TextInput(
                label=f"No Shares are {self.no_price} - You have ${self.curr_bb}", 
                placeholder="How much would you like to bet?",
                style=discord.TextStyle.short
            )
            self.add_item(self.buy_no)
        except Exception as e:
            print(f"Error in Buy_yes init: {e}")

    async def on_submit(self, interaction: discord.Interaction):
        try:    
                
                bb_spent = float(self.buy_no.value)
                new_bb = self.curr_bb - bb_spent
                if new_bb >= 0:
                    shares = bb_spent / float(self.no_price)
                    current_date = date.today()
                    answer = 'no'
                    with sqlite3.connect(self.parent_view.db_path) as connection:
                        cursor = connection.cursor()
                        cursor.execute("INSERT INTO transactions "
                        "(BetterBucks_Before, "
                        "BetterBucks_Spent, "
                        "Shares_Purchased, "
                        "User, "
                        "Event, "
                        "Question, "
                        "Answer, "
                        "BetterBucks_After, "
                        "Date, Resolve_Date) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (self.curr_bb,bb_spent,shares, self.parent_view.member_id,self.parent_view.event['title'],self.question, answer,new_bb,current_date, self.parent_view.end_date)
                        )
                        cursor.execute("UPDATE Users SET BetterBucks = ? WHERE User_id = ? AND Guild_id = ?",
                        (new_bb, self.parent_view.member_id, self.parent_view.guild_id))

                        connection.commit()
                        await interaction.response.send_message(f"Bet placed: ${bb_spent} on Yes at {self.no_price}. Bet will resolve on {self.parent_view.end_date}.")
                if new_bb < 0:
                    await interaction.response.send_message("You don't have enough BetterBucks for that. Are you poor?", ephemeral=True)
        except Exception as e:
                print(f"Error in Buy_no on_submit: {e}")
                await interaction.response.send_message("Something went wrong. ping @mrmeatbones", ephemeral=True)


class PaginatedView(discord.ui.View):
    def __init__(self, embed_data, polymarket_cog, timeout=60):
        super().__init__(timeout=timeout)
        self.embed_data = embed_data  
        self.polymarket_cog = polymarket_cog
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embed_data) - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.embed_data[self.current_page][0], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embed_data) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.embed_data[self.current_page][0], view=self)

    @discord.ui.button(label="Buy Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            _, yes_price, _, question = self.embed_data[self.current_page]
            modal = Buy_yes(parent_view=self.polymarket_cog, yes_price=yes_price, question=question)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"Error in yes_button: {e}")

    @discord.ui.button(label="Buy No", style=discord.ButtonStyle.red,)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            _, _, no_price, question = self.embed_data[self.current_page]
            modal = Buy_no(parent_view=self.polymarket_cog, no_price=no_price, question=question)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"Error in no_button: {e}")


class Polymarket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./config/db/Polymarket.db"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name="polymarket", description="View spread of a specific market and place a bet")
    async def polymarket(self, interaction: discord.Interaction, event_title: str):
        await interaction.response.defer()
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild.id

        r = requests.get(
            "https://gamma-api.polymarket.com/events?limit=1000&active=true&closed=false&order=liquidity&ascending=false",
            timeout=60
        )
        print(f"Status Code: {r.status_code}")
        r.raise_for_status()
        response = r.json()
        embed_data = [] 
        self.end_date = "N/A"

        for self.event in response:
            if self.event['title'].lower() == event_title.lower():
                for i, market in enumerate(self.event['markets'], 1):
                    question = market.get('question', 'N/A')
                    outcome_prices_str = market.get('outcomePrices', '["N/A", "N/A"]')
                    volume = market.get('volume', '0')
                    self.end_date = market.get('endDate', 'N/A')

                    try:
                        outcome_prices = json.loads(outcome_prices_str)
                        yes_price = round(float(outcome_prices[0] if len(outcome_prices) > 0 else 'N/A'),2)
                        no_price = round(float(outcome_prices[1] if len(outcome_prices) > 0 else 'N/A'),2)
                    except (json.JSONDecodeError, TypeError):
                        yes_price, no_price = 'N/A', 'N/A'

                    if yes_price == 'N/A' and no_price == 'N/A' and volume == '0':
                        continue
                    if yes_price == 1.0 and no_price == 0.0 or yes_price == 0.0 and no_price == 1.0:
                        continue
                    embed = discord.Embed(
                        title=f"Market {i} for \"{self.event['title']}\"",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Question", value=question, inline=False)
                    embed.add_field(name="Outcome Prices", value=f"Yes: {yes_price}\nNo: {no_price}", inline=True)
                    embed.add_field(name="Volume", value=f"${float(volume):,.2f}", inline=True)
                    embed.set_footer(text=f"Resolves after {self.end_date} | Page {i}/{len(self.event['markets'])}")

                    embed_data.append((embed, yes_price, no_price, question))

                break
        else:
            await interaction.followup.send(f"No active event found with the title '{event_title}'.", ephemeral=True)
            return

        if not embed_data:
            await interaction.followup.send("No markets available for this event.", ephemeral=True)
            return

        view = PaginatedView(embed_data, self)
        await interaction.followup.send(embed=embed_data[0][0], view=view)


async def setup(bot):
    await bot.add_cog(Polymarket(bot), guilds=[GUILD_ID])