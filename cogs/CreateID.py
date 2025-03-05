import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from main import GUILD_ID
import sqlite3

class CreateID(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./config/db/Exorcists.db"
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    async def createid(self, interaction: discord.Interaction, cid: str):
        try:
            
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Name, XID, Agenda, Blastphemy, Image, Sex, Height, Weight, Hair, Eyes, Cat_Rating FROM Exorcists WHERE CID = ?", (cid,))
                result = cursor.fetchone()

            img = Image.open('./config/images/IDCard.png')

            url = result[4]
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  
            pfp = Image.open(BytesIO(response.content)).convert("RGBA")
            output_path = f'./config/images/{cid}.png'
            size = (167, 207)

            
            pfp_resized = pfp.resize(size, Image.Resampling.LANCZOS)

           
            myFont = ImageFont.truetype('arial.ttf', 20)
            Font2 = ImageFont.truetype('arial.ttf', 65)

           
            I1 = ImageDraw.Draw(img)
            I1.text((228, 77), result[0], font=myFont, fill=(0, 0, 0))
            I1.text((272, 110), result[1], font=myFont, fill=(0, 0, 0))
            I1.text((269, 154), result[2], font=myFont, fill=(0, 0, 0))
            I1.text((269, 170), result[3], font=myFont, fill=(0, 0, 0))
            I1.text((251, 195), result[5], font=myFont, fill=(0, 0, 0))
            I1.text((251, 212), result[6], font=myFont, fill=(0, 0, 0))
            I1.text((251, 228), result[7], font=myFont, fill=(0, 0, 0))
            I1.text((400, 194), result[8], font=myFont, fill=(0, 0, 0))
            I1.text((400, 212), result[9], font=myFont, fill=(0, 0, 0))
            I1.text((396, 62), result[10], font=Font2, fill=(0, 0, 0))
            I1.text((241, 280), cid, font=myFont, fill=(0, 0, 0))

            
            midpoint = './config/images/ID2.png'
            img.save(midpoint)

            img2 = Image.open(midpoint)
            img2.paste(pfp_resized, (40, 52), mask=pfp_resized)
            img2.save(output_path)

            file = discord.File(output_path)
            await interaction.user.send(file=file)
            await interaction.response.send_message(f"Your Registration Number Is {cid}, And your ID has been mailed to you. Until The Stain Is Wiped Away", ephemeral=True)

        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(CreateID(bot), guilds=[GUILD_ID])