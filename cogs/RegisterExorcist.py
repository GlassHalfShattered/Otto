import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID
import sqlite3
from random import randint
import re


# Modals
class RegisterExorcistModal(discord.ui.Modal):
    def __init__(self, db_path, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.name = discord.ui.TextInput(label="Name", placeholder="First And Lastt",required=True, max_length=14, style=discord.TextStyle.short)
        self.XID = discord.ui.TextInput(label="XID", placeholder="Format: X0NN (e.g, X012)",required=True, max_length=4, style=discord.TextStyle.short)
        self.AGNDA = discord.ui.TextInput(label="Agenda", placeholder="Enter your current agenda",required=True, max_length=12, style=discord.TextStyle.short)
        self.BLSPH = discord.ui.TextInput(label="Blastphemy", placeholder="Enter your current blastphemy",required=True, max_length=12, style=discord.TextStyle.short)
        self.image = discord.ui.TextInput(label="Affix Photo", placeholder="HTTPS Link Required",required=True, style=discord.TextStyle.long)

        self.add_item(self.name)
        self.add_item(self.XID)
        self.add_item(self.AGNDA)
        self.add_item(self.BLSPH)
        self.add_item(self.image)

    async def on_submit(self, interaction: discord.Interaction):
        
        if not (self.XID.value.startswith("X0") and len(self.XID.value) == 4 and self.XID.value[2:].isdigit()) or  not self.image.value.startswith("https") :
            view = Step1retry(self.db_path)
            await interaction.response.send_message("XID must bein in the format 'XONN' where NN are two digits (e.g, X012). Affix Photo must be an HTTPS link. Please click the button to try again.",view=view, ephemeral=True)
        try:
            with sqlite3.connect(self.db_path) as connection:
                user = interaction.user.name
                status = "alive"
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Exorcists (Name, XID, Agenda, Blastphemy, Image, Player, Status) VALUES (?,?,?,?,?,?,?)", 
                (self.name.value, self.XID.value, self.AGNDA.value, self.BLSPH.value, self.image.value, user, status))
                self.exorcist_id = cursor.lastrowid
                connection.commit()
                
            view = Step2Button(self.db_path, self.exorcist_id)
            await interaction.response.send_message(f"Step 1 complete! Name: {self.name.value}, XID: {self.XID.value}. Click below for Step 2.",view=view, ephemeral=True)
        except Exception as e:
            print(f'Step 1: {e}')
            await interaction.response.send_message("An error occurred during registration.", ephemeral=True)

class Step2(discord.ui.Modal):
    def __init__(self, db_path, exorcist_id, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
        self.sex = discord.ui.TextInput(label="Sex", placeholder="Male/Female/Enby",required=True, max_length=6, style=discord.TextStyle.short)
        self.height = discord.ui.TextInput(label="Height", placeholder="x'y\"(e.g, 6'1\")",required=True, max_length=6, style=discord.TextStyle.short)
        self.weight = discord.ui.TextInput(label="Weight", placeholder="Enter weight in lb or kg, specify (e.g, 90lb)",required=True, max_length=6, style=discord.TextStyle.short)
        self.hair = discord.ui.TextInput(label="Hair", placeholder="If Applicable",required=True, max_length=20, style=discord.TextStyle.short)
        self.eyes = discord.ui.TextInput(label="Eye Colour", placeholder="If Applicable",required=True, max_length=20, style=discord.TextStyle.short)

        self.add_item(self.sex)
        self.add_item(self.height)
        self.add_item(self.weight)
        self.add_item(self.hair)
        self.add_item(self.eyes)

    async def on_submit(self, interaction: discord.Interaction):
        if not re.match(r"^\d+'[0-1]?\d?\"$", self.height.value):
            view = Step2retry(self.db_path, self.exorcist_id)

            await interaction.response.send_message(
                "Height must be in the format x'y\" where x is feet and y is inches (e.g., \"6'1\"\" or \"12'11\"\"). Please click the button to try again",view=view, ephemeral=True)

            return
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Sex=?, Height=?, Weight=?, Hair=?, Eyes=? WHERE id=?", 
                (self.sex.value, self.height.value, self.weight.value, self.hair.value, self.eyes.value, self.exorcist_id))
                connection.commit()
            view = Step3Button(self.db_path, self.exorcist_id)
            await interaction.response.send_message(f"Step 2 complete! Click below for Step 3.",view=view, ephemeral=True)
        except Exception as e:
            print(f'Step 2: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

class Step3(discord.ui.Modal):
    def __init__(self, db_path, exorcist_id, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
        self.force = discord.ui.TextInput(label="Force", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.conditioning = discord.ui.TextInput(label="Conditioning", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.coordination = discord.ui.TextInput(label="Coordination", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.covert = discord.ui.TextInput(label="Covert", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.interfacing = discord.ui.TextInput(label="Interfacing", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)

        self.add_item(self.force)
        self.add_item(self.conditioning)
        self.add_item(self.coordination)
        self.add_item(self.covert)
        self.add_item(self.interfacing)

    async def on_submit(self, interaction: discord.Interaction):
        allowed_values = {"0","1", "2", "3"}
        view = Step3retry(self.db_path, self.exorcist_id)

        if self.force.value not in allowed_values or self.conditioning.value not in allowed_values or self.coordination.value not in allowed_values or self.covert.value not in allowed_values or self.interfacing.value not in allowed_values:
            await interaction.response.send_message(
            "Skill values must be input as 1, 2 or 3. Please click the button to try again",view=view, ephemeral=True)

            return

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Force=?, Conditioning=?, Coordination=?, Covert=?, Interfacing=? WHERE id=?", 
                (self.force.value, self.conditioning.value, self.coordination.value, self.covert.value, self.interfacing.value, self.exorcist_id))
                connection.commit()
            view = Step4Button(self.db_path, self.exorcist_id)
            await interaction.response.send_message(f"Step 3 complete! Click below for Step 4.",view=view, ephemeral=True)
        except Exception as e:
            print(f'Step 3: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

class Step4(discord.ui.Modal):
    def __init__(self, db_path, exorcist_id, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
        self.investigation = discord.ui.TextInput(label="Investigation", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.surveillance = discord.ui.TextInput(label="Surveillance", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.negotiation = discord.ui.TextInput(label="Negotiation", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.authority = discord.ui.TextInput(label="Authority", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.connection = discord.ui.TextInput(label="Connection", placeholder="Enter your amount of points from 0-6 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)

        self.add_item(self.investigation)
        self.add_item(self.surveillance)
        self.add_item(self.negotiation)
        self.add_item(self.authority)
        self.add_item(self.connection)

    async def on_submit(self, interaction: discord.Interaction):
        view = Step4retry(self.db_path, self.exorcist_id)
        allowed_values = {"0","1", "2", "3"}
        if self.investigation.value not in allowed_values or self.surveillance.value not in allowed_values or self.negotiation.value not in allowed_values or self.authority.value not in allowed_values or self.connection.value not in allowed_values:
            await interaction.response.send_message(
            "Skill values must be input as 1, 2 or 3.",view=view, ephemeral=True)
            return
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Investigation=?, Surveillance=?, Negotiation=?, Authority=?, Connection=? WHERE id=?", 
                (self.investigation.value, self.surveillance.value, self.negotiation.value, self.authority.value, self.connection.value, self.exorcist_id))
                connection.commit()
            view = Step5Button(self.db_path, self.exorcist_id)
            await interaction.response.send_message(f"Step 4 complete! Click below for Step 5.",view=view, ephemeral=True)
        except Exception as e:
            print(f'Step 4: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

class Step5(discord.ui.Modal):
    def __init__(self, db_path, exorcist_id, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
        self.stress = discord.ui.TextInput(label="Stress", placeholder="Enter current stress from 0-6 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.injuries = discord.ui.TextInput(label="Injuries", placeholder="Enter current injuries from 0-4 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.afflictions = discord.ui.TextInput(label="Afflictions", placeholder="Enter your current afflctions. N/A if none.",required=True, style=discord.TextStyle.paragraph)
        self.crating = discord.ui.TextInput(label="Category Rating", placeholder="Enter current cat rating from 1-7 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.aitems = discord.ui.TextInput(label="Agenda Items", placeholder="Enter your current agenda items",required=True, style=discord.TextStyle.paragraph)

        self.add_item(self.stress)
        self.add_item(self.injuries)
        self.add_item(self.afflictions)
        self.add_item(self.crating)
        self.add_item(self.aitems)

    async def on_submit(self, interaction: discord.Interaction):
        view = Step5retry(self.db_path, self.exorcist_id)
        allowed_values = {"0","1", "2", "3", "4"}
        stress_value = {"0","1", "2", "3", "4", "5", "6"}
        cat_rating = {"1","2","3","4","5","6","7"}

        if self.injuries.value not in allowed_values or  self.stress.value not in stress_value or self.crating.value not in cat_rating:
            await interaction.response.send_message(
            "Injuries must be a value of 0-4. Stress must be a value of 0-6. Cat Rating must be between 1-7. Please click the button to try again.",view=view, ephemeral=True)
            return
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Stress=?, Injuries=?, Afflictions=?, Cat_Rating=?, Agenda_Items=? WHERE id=?",
                (self.stress.value, self.injuries.value, self.afflictions.value, self.crating.value, self.aitems.value, self.exorcist_id))
                connection.commit()
            view = Step6Button(self.db_path, self.exorcist_id)
            await interaction.response.send_message(f"Step 5 complete! Click below for Step 6.",view=view, ephemeral=True)
        except Exception as e:
            print(f'Step 5: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

class Step6(discord.ui.Modal):
    def __init__(self, db_path, exorcist_id, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
        self.aabilities = discord.ui.TextInput(label="Agenda Abilities", placeholder="Enter your current agenda abilities",required=True, style=discord.TextStyle.paragraph)
        self.power0 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=True, style=discord.TextStyle.paragraph)
        self.power1 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=False, style=discord.TextStyle.paragraph)
        self.power2 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=False, style=discord.TextStyle.paragraph)
        self.power3 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=False, style=discord.TextStyle.paragraph)
        self.add_item(self.aabilities)
        self.add_item(self.power0)
        self.add_item(self.power1)
        self.add_item(self.power2)
        self.add_item(self.power3)

    async def on_submit(self, interaction: discord.Interaction):
        view = Step6retry(self.db_path, self.exorcist_id)
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Agenda_Abilities=?, Observed_Power0 =?, Observed_Power1=?, Observed_Power2 =?, Observed_Power3 =? WHERE id=?", 
                (self.aabilities.value, self.power0.value, self.power1.value,self.power2.value,self.power3.value, self.exorcist_id))
                connection.commit()
            view = Step7Button(self.db_path, self.exorcist_id)
            await interaction.response.send_message(f"Step 6 complete! Click below for Step 7.",view=view, ephemeral=True)
        except Exception as e:
            print(f'Step 6: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

class Step7(discord.ui.Modal):
    def __init__(self, db_path, exorcist_id, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
        self.power4 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required = False,style=discord.TextStyle.paragraph)
        self.q1 = discord.ui.TextInput(label="How Did Your Powers First Manifest?", placeholder="",style=discord.TextStyle.paragraph)
        self.q2 = discord.ui.TextInput(label="Is Your Sin-Seed In Your Brain Or Heart?", placeholder="",style=discord.TextStyle.paragraph)
        self.q3 = discord.ui.TextInput(label="What Do You Hide In The Deepest Part Of You?", placeholder="",style=discord.TextStyle.paragraph)
        self.q4 = discord.ui.TextInput(label="Is Your Hand Your Hand?", placeholder="",style=discord.TextStyle.paragraph)

        self.add_item(self.power4)
        self.add_item(self.q1)
        self.add_item(self.q2)
        self.add_item(self.q3)
        self.add_item(self.q4)


    async def on_submit(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Observed_Power4=?, Q1=?, Q2=?, Q3=?, Q4=? WHERE id=?",
                 (self.power4.value, self.q1.value, self.q2.value, self.q3.value,self.q4.value, self.exorcist_id))
                connection.commit()
            view = Step8Button(self.db_path, self.exorcist_id)
            await interaction.response.send_message(f"Step 7 complete! Click below for Step 8.", view=view, ephemeral=True)
        except Exception as e:
            print(f'Step 7: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

class Step8(discord.ui.Modal):
    def __init__(self, db_path, exorcist_id, title="RegisterExorcist"):
        super().__init__(title=title)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
        self.q5 = discord.ui.TextInput(label="Do You Remember The Face Of Your Mother?", placeholder="",style=discord.TextStyle.paragraph)
        self.last = discord.ui.TextInput(label="Are You Sure?", placeholder="",style=discord.TextStyle.paragraph)
        self.add_item(self.q5)
      

    async def on_submit(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                CID = (f'XXX{randint(100000, 999999)}')
                cursor.execute("UPDATE Exorcists SET Q5=? , CID=? WHERE id=?", 
                (self.q5.value, CID, self.exorcist_id))
                connection.commit()
            id_cog = interaction.client.get_cog('CreateID')
            if id_cog:
                await id_cog.createid(interaction, CID)
                await interaction.user.send(f"Your Registration Number Is {CID}")
            else:
                await interaction.response.send_message(f"Your Registration Number Is {CID} (CreateID cog not found)", ephemeral=True)

           
        except Exception as e:
            print(f'Step 8: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

# Success Buttons




class Step2Button(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
    
    @discord.ui.button(label="Continue to Step 2", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step2(self.db_path, self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step3Button(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
    
    @discord.ui.button(label="Continue to Step 3", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step3(self.db_path, self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)



class Step4Button(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
    
    @discord.ui.button(label="Continue to Step 4", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step4(self.db_path, self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step5Button(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
    
    @discord.ui.button(label="Continue to Step 5", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step5(self.db_path, self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step6Button(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
    
    @discord.ui.button(label="Continue to Step 6", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step6(self.db_path, self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step7Button(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
    
    @discord.ui.button(label="Continue to Step 7", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step7(self.db_path, self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step8Button(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id
    
    @discord.ui.button(label="Continue to Step 8", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step8(self.db_path, self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)
#Retry Buttons
class Step1retry(discord.ui.View):
    def __init__(self, db_path):
        super().__init__(timeout=None)
        self.db_path = db_path
    
    @discord.ui.button(label="Retry step 1", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegisterExorcistModal(self.db_path,))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step2retry(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id


    @discord.ui.button(label="Retry step 2", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step2(self.db_path,self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step3retry(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id


    @discord.ui.button(label="Retry step 3", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step3(self.db_path,self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step4retry(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id


    @discord.ui.button(label="Retry step 4", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step4(self.db_path,self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step5retry(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id


    @discord.ui.button(label="Retry step 5", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step5(self.db_path,self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step6retry(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id


    @discord.ui.button(label="Retry step 6", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step6(self.db_path,self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step7retry(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id


    @discord.ui.button(label="Retry step 7", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step7(self.db_path,self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)

class Step8retry(discord.ui.View):
    def __init__(self, db_path, exorcist_id):
        super().__init__(timeout=None)
        self.db_path = db_path
        self.exorcist_id = exorcist_id


    @discord.ui.button(label="Retry step 8", style=discord.ButtonStyle.primary)
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Step8(self.db_path,self.exorcist_id))
        self.stop()
        await interaction.edit_original_response(view=None)
class CainSheet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./config/db/Exorcists.db"



    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name="register_exorcist", description="This will bring up 8 modals for data entry. Please read fields carefully.")
    async def register_exorcist(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RegisterExorcistModal(self.db_path))


    @app_commands.command(name="view_id", description="Retrieve your ID")
    async def View_ID(self, interaction: discord.Interaction,  cid: str):
        try:
            file_path = f'./config/images/{cid}.png'
            file = discord.File(file_path)
            await interaction.response.send_message(file=file)

        except Exception as e:
            await interaction.response.send_message(f"{cid} Is not a valid registration number. Please try again.")

async def setup(bot):
    await bot.add_cog(CainSheet(bot), guilds=[GUILD_ID])
