import requests
import json
import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID
import sqlite3
from datetime import date
from dotenv import load_dotenv
import aiocron
import os



class Betcheck(commands.Cog):
    def __init__(self, bot):
        load_dotenv()
        self.bot = bot
        self.db_path = "./config/db/polymarket.db"
        self.channel = int(os.getenv('CHANNEL_ID'))
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')
        self.cron = aiocron.crontab('0 3 * * *', func=self.check_bets, start=True)

    async def check_bets(self,):
        current_date = date.today()
        channel = self.bot.get_channel(self.channel)
        message = await channel.send("Checking For Winners and Losers")
        thread = await message.create_thread(name = f"{current_date}")
        
          
          
        with sqlite3.connect(self.db_path) as connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT Event, User_id, Question, Shares_Purchased, Answer FROM transactions WHERE Resolve_date < CURRENT_DATE AND Resolved = 'NO'")
                result = cursor.fetchall()
                cursor.execute("UPDATE transactions SET Resolved = 'YES' WHERE Resolve_date < CURRENT_DATE")
                sql_events = [row[0] for row in result]
                r = requests.get("https://gamma-api.polymarket.com/events?limit=1000&active=true&closed=true&order=closedTime&ascending=false",timeout=60)
                print(f"Status Code: {r.status_code}")
                r.raise_for_status()
                response = r.json()
                matched_events = [event for event in response if event['title'] in sql_events]

                for event in matched_events:
                    print(f"Event Title: {event['title']}")
                    bet_count = sql_events.count(event['title'])               
                    print(f"Number of bets on this event: {bet_count}")

                    market_outcomes = {}
                    for index,market in enumerate(event['markets'], 1):
                        question = market.get('question')
                        outcome_prices_str= market.get('outcomePrices')
                        outcome_prices = json.loads(outcome_prices_str)
                        yes = float(outcome_prices[0]) if outcome_prices[0] != "N/A" else 0.0
                        no = float(outcome_prices[1]) if outcome_prices[1] != "N/A" else 0.0
                        print(f'Question: {question} Yes: {yes} No: {no}')
                        winning_answer = 'yes' if yes == 1.0 else 'no' if no == 1.0 else 'unresolved'
                        market_outcomes[question] = winning_answer

                    for transaction in result:
                        if len(transaction) != 5:
                            print(f"Skipping malformed row: {transaction}, Length: {len(transaction)}")
                            continue
                        trans_event, user, trans_question, shares, answer = transaction
                        if trans_event == event['title']:
                            winning_answer = market_outcomes.get(trans_question, 'unresolved')
                            if winning_answer != 'unresolved':
                                did_win = (answer.lower() == winning_answer)
                                
                                if did_win:
                                        try:
                                            cursor.execute("SELECT BetterBucks, User_Name FROM Users WHERE User_id = ?",(user,))
                                            user_data= cursor.fetchone()
                                            curr_bb = round(user_data[0],2)
                                            new_bb = round((shares + curr_bb),2)
                                            name = user_data[1]
                                            cursor.execute("UPDATE Users SET BetterBucks = ? WHERE User_id = ?",(new_bb,user))
                                            cursor.execute("UPDATE Transactions SET Win = 'Yes' WHERE User_id = ? AND Event = ? AND Question = ? ",(user,trans_event,trans_question))

                                            #print(f"{name} Won {shares} BetterBucks By Correctly Guessing If `{question}` Their New Balance Is {new_bb}")
                                            await thread.send(f"{name} Won {shares} BetterBucks By Correctly Guessing If `{question}` Their New Balance Is {new_bb}")
                                        except Exception as e:
                                            print(f'error picking winners{e}')
                                else: 
                                        try:
                                            cursor.execute("SELECT User_Name FROM Users WHERE User_id = ?",(user,))
                                            user_data = cursor.fetchone()
                                            name = user_data[0]
                                            cursor.execute("UPDATE Transactions SET Win = 'No' WHERE User_id = ? AND Event = ? AND Question = ? ",(user,trans_event,trans_question))
                                            #print(f"{name} Lost {shares} BetterBucks On `{question}` What A Loser")
                                            await thread.send(f"{name} Lost {shares} BetterBucks On `{question}` What A Loser")
                                        except Exception as e:
                                            print(f'error picking losers{e}')
                connection.commit()
            except Exception as e:
                print(f"Error in check_bets: {e}")

async def setup(bot):
    await bot.add_cog(Betcheck(bot), guilds=[GUILD_ID])