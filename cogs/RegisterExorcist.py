# cogs/ping.py
import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID
import sqlite3
from random import randint
import re

def initialize_db(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Exorcists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT, XID TEXT, Agenda TEXT, Blastphemy TEXT, Image TEXT,
                Player TEXT, Status TEXT,
                Sex TEXT, Height TEXT, Weight TEXT, Hair TEXT, Eyes TEXT,
                Force TEXT, Conditioning TEXT, Covert TEXT, Interfacing TEXT,
                Investigation TEXT, Surveillance TEXT, Negotiation TEXT,
                Authority TEXT, Connection TEXT, Improvement TEXT,
                Stress TEXT, Injuries TEXT, Hooks TEXT, Afflictions TEXT,
                Divine_Agony TEXT, XP TEXT, Advances TEXT, Cat_Rating TEXT,
                Psyche TEXT, Burst TEXT, Kit_Points TEXT, Agenda_Items TEXT,
                Agenda_Abilities TEXT, Observed_Power0 TEXT, Observed_Power1 TEXT,
                Observed_Power2 TEXT, Observed_Power3 TEXT, Observed_Power4 TEXT, CID TEXT, Sin TEXT, 
                Sin_Marks, TEXT, Registered Kit Text, Script TEXT, Q1 TEXT, Q2 TEXT, Q3 TEXT, Q4 TEXT, 
                Q5 TEXT, Q6 TEXT, Notes TEXT
            )
        ''')
        conn.commit()
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
                initialize_db(self.db_path)
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
        self.covert = discord.ui.TextInput(label="Covert", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.interfacing = discord.ui.TextInput(label="Interfacing", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.investigation = discord.ui.TextInput(label="Investigation", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)

        self.add_item(self.force)
        self.add_item(self.conditioning)
        self.add_item(self.covert)
        self.add_item(self.interfacing)
        self.add_item(self.investigation)

    async def on_submit(self, interaction: discord.Interaction):
        allowed_values = {"0","1", "2", "3"}
        view = Step3retry(self.db_path, self.exorcist_id)

        if self.force.value not in allowed_values or self.conditioning.value not in allowed_values or self.covert.value not in allowed_values or self.interfacing.value not in allowed_values or self.investigation.value not in allowed_values:
            await interaction.response.send_message(
            "Skill values must be input as 1, 2 or 3. Please click the button to try again",view=view, ephemeral=True)

            return

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Force=?, Conditioning=?, Covert=?, Interfacing=?, Investigation=? WHERE id=?", 
                (self.force.value, self.conditioning.value, self.covert.value, self.interfacing.value, self.investigation.value, self.exorcist_id))
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
        self.surveillance = discord.ui.TextInput(label="Surveillance", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.negotiation = discord.ui.TextInput(label="Negotiation", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.authority = discord.ui.TextInput(label="Authority", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.connection = discord.ui.TextInput(label="Connection", placeholder="Enter your amount of points from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.improvement = discord.ui.TextInput(label="Improvement", placeholder="Enter your amount of points from 0-6 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)

        self.add_item(self.surveillance)
        self.add_item(self.negotiation)
        self.add_item(self.authority)
        self.add_item(self.connection)
        self.add_item(self.improvement)

    async def on_submit(self, interaction: discord.Interaction):
        view = Step4retry(self.db_path, self.exorcist_id)
        allowed_values = {"0","1", "2", "3"}
        improvement_value = {"0","1", "2", "3", "4", "5", "6"}
        if self.surveillance.value not in allowed_values or self.negotiation.value not in allowed_values or self.authority.value not in allowed_values or self.connection.value not in allowed_values or self.improvement.value not in improvement_value:
            await interaction.response.send_message(
            "Skill values must be input as 1, 2 or 3. Improvment value must be between 0-6. Please click the button to try again",view=view, ephemeral=True)
            return
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Surveillance=?, Negotiation=?, Authority=?, Connection=?, Improvement=? WHERE id=?", 
                (self.surveillance.value, self.negotiation.value, self.authority.value, self.connection.value, self.improvement.value, self.exorcist_id))
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
        self.hooks = discord.ui.TextInput(label="Hooks", placeholder="Enter current hooks from 0-4 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.afflictions = discord.ui.TextInput(label="Afflictions", placeholder="Enter your current afflctions. N/A if none.",required=True, style=discord.TextStyle.paragraph)
        self.divine_agony = discord.ui.TextInput(label="Pathos", placeholder="Enter your current pathos from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)

        self.add_item(self.stress)
        self.add_item(self.injuries)
        self.add_item(self.hooks)
        self.add_item(self.afflictions)
        self.add_item(self.divine_agony)

    async def on_submit(self, interaction: discord.Interaction):
        view = Step5retry(self.db_path, self.exorcist_id)
        allowed_values = {"0","1", "2", "3", "4"}
        stress = {"0","1", "2", "3", "4", "5", "6"}
        pathos = {"1", "2", "3"}
        if self.injuries.value not in allowed_values or self.hooks.value not in allowed_values or self.stress.value not in stress or self.divine_agony.value not in pathos:
            await interaction.response.send_message(
            "Stress/injuries must be a value of 0-4. Stress must be a value of 0-6. Pathos must be a value of 0-3. Please click the button to try again.",view=view, ephemeral=True)
            return
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Stress=?, Injuries=?, Hooks=?, Afflictions=?, Divine_Agony=? WHERE id=?", 
                (self.stress.value, self.injuries.value, self.hooks.value, self.afflictions.value, self.divine_agony.value, self.exorcist_id))
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
        self.xp = discord.ui.TextInput(label="XP", placeholder="Enter current XP from 0-4 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.advances = discord.ui.TextInput(label="Advances", placeholder="Enter current stress from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.crating = discord.ui.TextInput(label="Category Rating", placeholder="Enter current cat rating from 0-7 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.psyche = discord.ui.TextInput(label="Psyche", placeholder="Enter current psyche points left from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)
        self.burst = discord.ui.TextInput(label="Burst", placeholder="Enter current cat rating from 0-3 (e.g, 2)",required=True, max_length=1, style=discord.TextStyle.short)

        self.add_item(self.xp)
        self.add_item(self.advances)
        self.add_item(self.crating)
        self.add_item(self.psyche)
        self.add_item(self.burst)

    async def on_submit(self, interaction: discord.Interaction):
        allowed_values = {"0","1", "2", "3"}
        cat_rating = {"0","1","2","3","4","5","6","7"}
        xp = {"0","1", "2", "3","4"}
        view = Step6retry(self.db_path, self.exorcist_id)
        if self.advances.value not in allowed_values or self.psyche.value not in allowed_values or self.burst.value not in allowed_values or self.crating.value not in cat_rating or self.xp.value not in xp:
            await interaction.response.send_message(
            "Xp must be a value of 0-4. Advances must be a value of 0-3. Category Rating must be a value of 0-7. Psyche/Burst must be a value of 0-3. Please click the button to try again.",view=view, ephemeral=True)
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET XP=?, Advances=?, Cat_Rating=?, Psyche=?, Burst=? WHERE id=?", 
                (self.xp.value, self.advances.value, self.crating.value, self.psyche.value, self.burst.value, self.exorcist_id))
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
        self.kit = discord.ui.TextInput(label="Kit Points", placeholder="Enter your current available kit points from 0-9",required=True, max_length=100, style=discord.TextStyle.short)
        self.aitems = discord.ui.TextInput(label="Agenda Items", placeholder="Enter your current agenda items",required=True, style=discord.TextStyle.paragraph)
        self.aabilities = discord.ui.TextInput(label="Agenda Abilities", placeholder="Enter your current agenda abilities",required=True, style=discord.TextStyle.paragraph)
        self.power1 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=True, style=discord.TextStyle.paragraph)
        self.power2 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=True, style=discord.TextStyle.paragraph)

        self.add_item(self.kit)
        self.add_item(self.aitems)
        self.add_item(self.aabilities)
        self.add_item(self.power1)
        self.add_item(self.power2)

    async def on_submit(self, interaction: discord.Interaction):
        kit = {"0","1", "2", "3","4","5","6", "7", "8", "9"}
        view = Step7retry(self.db_path, self.exorcist_id)
        if self.kit.value not in kit:
            await interaction.response.send_message(
            "Kit points must be a value of 0-9. Please click the button to try again.",view=view, ephemeral=True)

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Kit_Points=?, Agenda_Items=?, Agenda_Abilities=?, Observed_Power0=?, Observed_Power1=? WHERE id=?",
                 (self.kit.value, self.aitems.value, self.aabilities.value, self.power1.value, self.power2.value, self.exorcist_id))
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
        self.power3 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=True, max_length=100, style=discord.TextStyle.paragraph)
        self.power4 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=True, max_length=100, style=discord.TextStyle.paragraph)
        self.power5 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",required=True, max_length=100, style=discord.TextStyle.paragraph)
        self.add_item(self.power3)
        self.add_item(self.power4)
        self.add_item(self.power5)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                CID = (f'XXX{randint(100000, 999999)}')
                cursor.execute("UPDATE Exorcists SET Observed_Power2=?, Observed_Power3=?,Observed_Power4=? , CID=? WHERE id=?", 
                (self.power3.value, self.power4.value, self.power5.value, CID, self.exorcist_id))
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
        initialize_db(self.db_path)


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name="register_exorcist", description="This will bring up 8 modals for data entry. Please read fields carefully.")
    async def register_exorcist(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RegisterExorcistModal(self.db_path))

async def setup(bot):
    await bot.add_cog(CainSheet(bot), guilds=[GUILD_ID])
