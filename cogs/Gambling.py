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
                        "User_id, "
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
            print(f"Error in Buy_no init: {e}")

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
                        "User_id, "
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
                        await interaction.response.send_message(f"Bet placed: ${bb_spent} on No at {self.no_price}. Bet will resolve on {self.parent_view.end_date}.")
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
        self.db_path = "./config/db/polymarket.db"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name="polymarket", description="View spread of a specific market and place a bet")
    async def polymarket(self, interaction: discord.Interaction, url : str):
        await interaction.response.defer()
        print("Deferred response sent")
    
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild.id
        slug = url.split("event/")[1].split("?tid")[0]
        api_url = f"https://gamma-api.polymarket.com/events?limit=1000&active=true&slug={slug.lower()}&closed=false&order=liquidity&ascending=false"
        print(f"Requesting API: {api_url}")
        
        try:
                r = requests.get(api_url, timeout=5)  # Reduced timeout for faster failure
                print(f"Request completed with status: {r.status_code}")
                print(f"Response headers: {r.headers}")
                print(f"Raw response length: {len(r.text)} bytes")
                
                r.raise_for_status()
                response = r.json()
                print(f"JSON parsed successfully, item count: {len(response)}")
        
        except requests.Timeout:
                print("Request timed out")
                await interaction.followup.send("Request timed out. The API might be slow or unreachable.", ephemeral=True)
                return
        except requests.RequestException as e:
                print(f"Request failed: {e}")
                await interaction.followup.send(f"API error: {str(e)}", ephemeral=True)
                return
        except ValueError as e:
                print(f"JSON parsing failed: {e}")
                await interaction.followup.send("Error parsing API response.", ephemeral=True)
                return
        embed_data = []
        self.end_date = "N/A"
        print(f"Processing response with {len(response)} events")
        for self.event in response:
            print(f"Event slug: {self.event['slug']}, checking against: {slug}")
            if self.event['slug'].lower() == slug.lower():
                print(f"Found matching event, markets count: {len(self.event.get('markets', []))}")
                for i, market in enumerate(self.event['markets'], 1):
                    question = market.get('question', 'N/A')
                    outcome_prices_str = market.get('outcomePrices', '["N/A", "N/A"]')
                    volume = market.get('volume', '0')
                    self.end_date = market.get('endDate', 'N/A')
                    print(f"Market {i}: {question}, prices: {outcome_prices_str}")

                    try:
                        outcome_prices = json.loads(outcome_prices_str)
                        yes_price = round(float(outcome_prices[0] if len(outcome_prices) > 0 else 'N/A'),2)
                        no_price = round(float(outcome_prices[1] if len(outcome_prices) > 0 else 'N/A'),2)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        yes_price, no_price = 'N/A', 'N/A'

                    if yes_price == 'N/A' and no_price == 'N/A' and volume == '0':
                        print(f"Skipping market {i}: all N/A and zero volume")
                        continue
                    if yes_price == 1.0 and no_price == 0.0 or yes_price == 0.0 and no_price == 1.0:
                        print(f"Skipping market {i}: resolved market")
                        continue
                    embed = discord.Embed(
                        title=f"Market {i} for \"{self.event['title']}\"",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Question", value=question, inline=False)
                    embed.add_field(name="Outcome Prices", value=f"Yes: {yes_price}\nNo: {no_price}", inline=True)
                    embed.add_field(name="Volume", value=f"${float(volume):,.2f}", inline=True)
                    embed.set_footer(text=f"Resolves after {self.end_date} | Page {i}/{len(self.event['markets'])}")
                    print(f"Added market {i} to embed_data")

                    embed_data.append((embed, yes_price, no_price, question))

                break
        else:
            print("No matching event found")
            await interaction.followup.send(f"No active event found with the title '{slug}'.", ephemeral=True)
            return

        if not embed_data:
            print("No markets available")
            await interaction.followup.send("No markets available for this event.", ephemeral=True)
            return
        print("Creating PaginatedView")
        view = PaginatedView(embed_data, self)
        print("Sending follow-up with embed")
        await interaction.followup.send(embed=embed_data[0][0], view=view)
        print("Follow-up sent successfully")


async def setup(bot):
    await bot.add_cog(Polymarket(bot), guilds=[GUILD_ID])