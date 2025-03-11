import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID
import sqlite3
import math



class Afflictions(discord.ui.Modal, title="Afflictions"):
    def __init__(self, parent_view: 'SheetView'):
        super().__init__()
        self.parent_view = parent_view
        with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Afflictions FROM Exorcists WHERE CID = ?", (self.parent_view.cid,))
                result = cursor.fetchone()
                curr_aff = result[0] if result else "None"
        self.afflictions = discord.ui.TextInput(label="Afflictions", placeholder="Update Afflictions",style=discord.TextStyle.paragraph, default=curr_aff)
        self.add_item(self.afflictions)



    async def on_submit(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Afflictions = ? WHERE CID = ?", (self.afflictions.value, self.parent_view.cid))
                connection.commit()
                await self.parent_view.refresh_embeds(interaction, self.parent_view.stress)

           
        except Exception as e:
            print(f'Afflictions: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)


class Registered_Kit(discord.ui.Modal, title="Registered_Kit"):
    def __init__(self, parent_view: 'SheetView'):
        super().__init__()
        self.parent_view = parent_view
        with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Kit_Items FROM Exorcists WHERE CID = ?", (self.parent_view.cid,))
                result = cursor.fetchone()
                curr_gear = result[0] if result else "None"
        self.gear = discord.ui.TextInput(label="Registered Kit", placeholder="Update Gear",style=discord.TextStyle.paragraph, default=curr_gear)
        self.add_item(self.gear)



    async def on_submit(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Kit_Items = ? WHERE CID = ?", (self.gear.value, self.parent_view.cid))
                connection.commit()
                await self.parent_view.refresh_embeds(interaction, self.parent_view.stress)

           
        except Exception as e:
            print(f'Gear: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

    

class Update_powers(discord.ui.Modal, title="Update Powers"):
    def __init__(self, parent_view: 'SheetView'):
        super().__init__()
        self.parent_view = parent_view
        with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Observed_Power0, Observed_Power1, Observed_Power2, Observed_Power3, Observed_Power4 FROM Exorcists WHERE CID = ?", (self.parent_view.cid,))
                result = cursor.fetchone()
                powerone = result[0] if result else "None"
                powertwo = result[1] if result else "None"
                powerthree = result[2] if result else "None"
                powerfour = result[3] if result else "None"
                powerfive = result[4] if result else "None"
        self.parent_view = parent_view
        self.power0 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable",style=discord.TextStyle.paragraph, default=powerone)
        self.power1 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable", style=discord.TextStyle.paragraph, default=powertwo)
        self.power2 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable", style=discord.TextStyle.paragraph, default=powerthree)
        self.power3 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable", style=discord.TextStyle.paragraph, default=powerfour)
        self.power4 = discord.ui.TextInput(label="Observed Power", placeholder="Enter Observed Power If Applicable", style=discord.TextStyle.paragraph, default=powerfive)
        self.add_item(self.power0)
        self.add_item(self.power1)
        self.add_item(self.power2)
        self.add_item(self.power3)
        self.add_item(self.power4)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.parent_view.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Exorcists SET Observed_Power0 = ?, Observed_Power1 = ?, Observed_Power2 = ?, Observed_Power3 = ?, Observed_Power4 = ? WHERE CID = ?", (self.power0.value, self.power1.value, self.power2.value,
                                    self.power3.value, self.power4.value, self.parent_view.cid))
                connection.commit()
                await self.parent_view.refresh_embeds(interaction, self.parent_view.stress)

           
        except Exception as e:
            print(f'Powers: {e}')
            await interaction.response.send_message("An error occurred.", ephemeral=True)

           
class HookAdjustView(discord.ui.View):
    def __init__(self, parent_view: 'SheetView', hook_num: int):
        super().__init__(timeout=60)  # 60-second timeout
        self.parent_view = parent_view
        self.hook_num = hook_num
        self.hook_field = f"HOOK{self.hook_num}"



    @discord.ui.button(label="Increase", style=discord.ButtonStyle.red)
    async def increase_hook(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                    with sqlite3.connect(self.parent_view.db_path) as connection:
                        cursor = connection.cursor()
                        cursor.execute(f"SELECT {self.hook_field} FROM Exorcists WHERE CID = ?", (self.parent_view.cid,))
                        result = cursor.fetchone()
                        if int(result[0]) < 3:  # Max hook value is 3
                            new_value = int(result[0]) + 1
                            cursor.execute(f"UPDATE Exorcists SET {self.hook_field} = ? WHERE CID = ?", (new_value, self.parent_view.cid))
                            connection.commit()
                            setattr(self.parent_view, f"hook{self.hook_num}", new_value)
                            await self.parent_view.refresh_embeds(interaction, self.parent_view.stress)
            except Exception as e:
                    print(e)



    @discord.ui.button(label="Decrease", style=discord.ButtonStyle.green)
    async def decrease_hook(self, interaction: discord.Interaction, button: discord.ui.Button):
        with sqlite3.connect(self.parent_view.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT {self.hook_field} FROM Exorcists WHERE CID = ?", (self.parent_view.cid,))
            result = cursor.fetchone()
            if  int(result[0]) > 0:  # Min hook value is 0
                new_value = int(result[0]) - 1
                cursor.execute(f"UPDATE Exorcists SET {self.hook_field} = ? WHERE CID = ?", (new_value, self.parent_view.cid))
                connection.commit()
                setattr(self.parent_view, f"hook{self.hook_num}", new_value)
                await self.parent_view.refresh_embeds(interaction, self.parent_view.stress)



    @discord.ui.button(label="Rename", style=discord.ButtonStyle.blurple)
    async def rename_hook(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HookRenameModal(self.parent_view, self.hook_num))



class HookRenameModal(discord.ui.Modal, title="Rename Hook"):
    def __init__(self, parent_view: 'SheetView', hook_num: int):
        super().__init__()
        self.parent_view = parent_view
        self.hook_num = hook_num
        self.hook_name = discord.ui.TextInput(
            label=f"New Hook {hook_num} Name",
            placeholder="Enter new hook name...",
            max_length=50
        )
        self.add_item(self.hook_name)



    async def on_submit(self, interaction: discord.Interaction):
        with sqlite3.connect(self.parent_view.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE Exorcists SET HOOK{self.hook_num}_NAME = ? WHERE CID = ?", 
                         (self.hook_name.value, self.parent_view.cid))
            connection.commit()
        await self.parent_view.refresh_embeds(interaction, self.parent_view.stress)













class SkillAdjustView(discord.ui.View):
    def __init__(self, parent_view: 'SheetView', skill_name: str):
        super().__init__(timeout=60)  # 60-second timeout
        self.parent_view = parent_view
        self.skill_name = skill_name


    @discord.ui.button(label="Increase", style=discord.ButtonStyle.green)
    async def increase_skill(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                    with sqlite3.connect(self.parent_view.db_path) as connection:
                        cursor = connection.cursor()
                        cursor.execute(f"SELECT {self.skill_name}, Improvements, Advancements FROM Exorcists WHERE CID = ?", (self.parent_view.cid,))
                        result = cursor.fetchone()
                        if int(result[0]) < 3 and int(result[1]) < 6 and int(result[2]) > 0:
                            skill_value = int(result[0]) + 1
                            imp_value = int(result[1]) + 1
                            adv_value = int(result[1]) - 1
                            cursor.execute(f"UPDATE Exorcists SET {self.skill_name} = ?, Improvements = ?, Advancements = ? WHERE CID = ?", (skill_value,imp_value, adv_value, self.parent_view.cid))
                            connection.commit()
                            setattr(self.parent_view, self.skill_name, skill_value)
                            await self.parent_view.refresh_embeds(interaction, self.parent_view.stress)
            except Exception as e:
                    print(e)



        



class SheetView(discord.ui.View):
    def __init__(self, embeds, interaction: discord.Interaction, cid: str, db_path: str):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.current_page = 0
        self.interaction = interaction
        self.message = None
        self.cid = cid
        self.db_path = db_path
        self.stress = 0
        self.injuries = 0
        self.max_stress = 6
        self.sin = 0
        self.sin_marks = None
        self.hook1 = 0
        self.hook2 = 0
        self.hook3 = 0
        self.afflictions = None
        self.force = 0
        self.conditioning = 0
        self.coordination = 0
        self.covert = 0
        self.interfacing = 0
        self.investigation = 0
        self.surveillance = 0
        self.negotiation = 0
        self.authority = 0
        self.con = 0
        self.improvemments = 0
        self.pathos = 0
        self.xp = 0
        self.advances = 0
        self.visrights = 0
        self.total_sin_marks = 0
        self.max_psyche = 0
        self.setup_buttons()  # Initial setup for page 0

    def setup_buttons(self):
        """Dynamically set up buttons based on the current page."""
        self.clear_items()  # Remove all existing buttons
        if self.current_page == 0:  # First page buttons
            self.add_item(discord.ui.Button(label="Stress-", style=discord.ButtonStyle.green, custom_id="stress_minus"))
            self.add_item(discord.ui.Button(label="Stress+", style=discord.ButtonStyle.red, custom_id="stress_plus"))
            self.add_item(discord.ui.Button(label="Sin-", style=discord.ButtonStyle.green, custom_id="sin_minus"))
            self.add_item(discord.ui.Button(label="Sin+", style=discord.ButtonStyle.red, custom_id="sin_plus"))
            self.add_item(discord.ui.Button(label="Remove Injury", style=discord.ButtonStyle.green, custom_id="injury_minus"))
            self.add_item(discord.ui.Button(label="Add Injury", style=discord.ButtonStyle.red, custom_id="injury_plus"))
            self.add_item(discord.ui.Button(label="Hooks", style=discord.ButtonStyle.blurple, custom_id="hooks_menu"))
            self.add_item(discord.ui.Button(label="Add Pathos", style=discord.ButtonStyle.red, custom_id="pathos_plus"))
            self.add_item(discord.ui.Button(label="Burn Pathos", style=discord.ButtonStyle.green, custom_id="burn_pathos"))
            self.add_item(discord.ui.Button(label="Gain XP", style=discord.ButtonStyle.green, custom_id="gain_xp"))
            self.add_item(discord.ui.Button(label="Skill Increase", style=discord.ButtonStyle.blurple, custom_id="skill_menu"))
            self.add_item(discord.ui.Button(label="Afflictions", style=discord.ButtonStyle.red, custom_id="afflictions"))
        elif self.current_page == 1:  # Second page buttons
            self.add_item(discord.ui.Button(label="Regain Psyche", style=discord.ButtonStyle.green, custom_id="psyche_minus"))
            self.add_item(discord.ui.Button(label="Consume Psyche", style=discord.ButtonStyle.red, custom_id="psyche_plus"))
            self.add_item(discord.ui.Button(label="Regain Burst", style=discord.ButtonStyle.green, custom_id="burst_minus"))
            self.add_item(discord.ui.Button(label="Consume Burst", style=discord.ButtonStyle.red, custom_id="burst_plus"))
            self.add_item(discord.ui.Button(label="Regain Kit Points", style=discord.ButtonStyle.green, custom_id="kit_minus"))
            self.add_item(discord.ui.Button(label="Consume Kit Points", style=discord.ButtonStyle.red, custom_id="kit_plus"))
            self.add_item(discord.ui.Button(label="Update Gear", style=discord.ButtonStyle.blurple, custom_id="reg_gear"))
        elif self.current_page == 2: # Third page buttons
            self.add_item(discord.ui.Button(label="Update Powers", style=discord.ButtonStyle.blurple, custom_id="update_powers"))
        elif self.current_page == 4: # Fith page buttons
            self.add_item(discord.ui.Button(label="Increase CAT", style=discord.ButtonStyle.green, custom_id="cat_plus"))
            self.add_item(discord.ui.Button(label="Increase Kit Modifier", style=discord.ButtonStyle.green, custom_id="kitmod_plus"))
            self.add_item(discord.ui.Button(label="Spend Scrip", style=discord.ButtonStyle.green, custom_id="scrip_minus"))
            self.add_item(discord.ui.Button(label="Gain Scrip", style=discord.ButtonStyle.green, custom_id="scrip_plus"))
            self.add_item(discord.ui.Button(label="Gain Visitation Rights", style=discord.ButtonStyle.green, custom_id="visitation"))
 






        # Always add navigation buttons
        self.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.grey, custom_id="previous"))
        self.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.grey, custom_id="next"))

    # Button callbacks
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Handle button interactions based on custom_id."""
        custom_id = interaction.data["custom_id"]
        
        if custom_id == "stress_minus":
            await self.stress_minus(interaction)
        elif custom_id == "stress_plus":
            await self.stress_plus(interaction)
        elif custom_id == "sin_minus":
            await self.sin_minus(interaction)
        elif custom_id == "sin_plus":
            await self.sin_plus(interaction)
        elif custom_id == "injury_minus":
            await self.injury_minus(interaction)
        elif custom_id == "injury_plus":
            await self.injury_plus(interaction)
        elif custom_id == "hooks_menu":
            await self.hooks_menu(interaction)
        elif custom_id == "pathos_plus":
            await self.pathos_plus(interaction)
        elif custom_id == "burn_pathos":
            await self.burn_pathos(interaction)
        elif custom_id == "gain_xp":
            await self.gain_xp(interaction)
        elif custom_id == "skill_menu":
            await self.skill_menu(interaction)
        elif custom_id == "afflictions":
            await self.show_afflictions(interaction)
        elif custom_id == "previous":
            await self.previous(interaction)
        elif custom_id == "next":
            await self.next(interaction)
        # Add new buttons for page 2 here
        elif custom_id == "psyche_minus":
            await self.psyche_minus(interaction)
        elif custom_id == "psyche_plus":
            await self.psyche_plus(interaction)
        elif custom_id == "burst_minus":
            await self.burst_minus(interaction)
        elif custom_id == "burst_plus":
            await self.burst_plus(interaction)
        elif custom_id == "kit_minus":
            await self.kit_minus(interaction)
        elif custom_id == "kit_plus":
            await self.kit_plus(interaction)
        elif custom_id == "reg_gear":
            await self.show_gear(interaction)
        # Add new buttons for page 3 here
        elif custom_id == "update_powers":
            await self.show_powers(interaction)
        # Add new buttons for page 4 here
        elif custom_id == "cat_plus":
            await self.cat_plus(interaction)
        elif custom_id == "scrip_minus":
            await self.scrip_minus(interaction)
        elif custom_id == "scrip_plus":
            await self.scrip_plus(interaction)
        elif custom_id == "visitation":
            await self.visitation_plus(interaction)
        elif custom_id == "kitmod_plus":
            await self.kitmod_plus(interaction)

        return True  # Allow the interaction to proceed

    #button methods
    async def stress_minus(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Stress FROM Exorcists WHERE CID = ?", (self.cid,))
            result = cursor.fetchone()
            if result is None:
                await interaction.response.send_message("Character not found.", ephemeral=True)
                return
            current_stress = int(result[0])  
            if current_stress > 0:
                new_stress = current_stress - 1
                cursor.execute("UPDATE Exorcists SET Stress = ? WHERE CID = ?", (new_stress, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, new_stress)

    async def stress_plus(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Stress, Injuries FROM Exorcists WHERE CID = ?", (self.cid,))
            result = cursor.fetchone()
            if result is None:
                await interaction.response.send_message("Character not found.", ephemeral=True)
                return
            current_stress = int(result[0]) 
            injuries = int(result[1]) 
            max_stress = 6 - injuries
            if current_stress < max_stress:
                new_stress = current_stress + 1
                cursor.execute("UPDATE Exorcists SET Stress = ? WHERE CID = ?", (new_stress, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, new_stress)

    async def sin_minus(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Sin FROM Exorcists WHERE CID = ?", (self.cid,))
            result = cursor.fetchone()
            if result is None:
                await interaction.response.send_message("Character not found.", ephemeral=True)
                return
            current_sin = int(result[0])  
            if current_sin > 0:
                new_sin = current_sin - 1
                cursor.execute("UPDATE Exorcists SET Sin = ? WHERE CID = ?", (new_sin, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, new_sin)

    async def sin_plus(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Sin, Total_Sin_Marks, ADD_BLSPH FROM Exorcists WHERE CID = ?", (self.cid,))
            result = cursor.fetchone()
            if result is None:
                await interaction.response.send_message("Character not found.", ephemeral=True)
                return
            current_sin = int(result[0]) 
            total_sin_marks = int(result[1]) 
            add_blsph = int(result[2])
            max_sin = 10 - total_sin_marks - add_blsph
            if current_sin < max_sin:
                new_sin = current_sin + 1
                cursor.execute("UPDATE Exorcists SET Sin = ? WHERE CID = ?", (new_sin, self.cid))
                connection.commit()
                if new_sin == max_sin:
                    try:
                        await self.sin_overflow(interaction)
                    except Exception as e:
                        print(e)
            await self.refresh_embeds(interaction, new_sin)

    async def injury_minus(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Injuries FROM Exorcists WHERE CID = ?", (self.cid,))
            result = cursor.fetchone()
            if result is None:
                await interaction.response.send_message("Character not found.", ephemeral=True)
                return
            current_injury = int(result[0])  
            if current_injury > 0:
                new_injury = current_injury - 1
                cursor.execute("UPDATE Exorcists SET Injuries = ? WHERE CID = ?", (new_injury, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, new_injury)

    async def injury_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Injuries FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                
                current_injury = int(result[0])
                if current_injury < 3:
                    new_injury = current_injury + 1
                    new_stress = 0
                    cursor.execute("UPDATE Exorcists SET Injuries = ?, Stress = ? WHERE CID = ?", (new_injury, new_stress, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, new_stress)
                else:
                    await interaction.response.send_message("This exorcist is dead")
        except Exception as e:
            print(e)

    async def hooks_menu(self, interaction: discord.Interaction):
        class HookSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Hook 1", value="1"),
                    discord.SelectOption(label="Hook 2", value="2"),
                    discord.SelectOption(label="Hook 3", value="3")
                ]
                super().__init__(placeholder="Select a Hook to adjust...", options=options)

            async def callback(self, select_interaction: discord.Interaction):
                hook_num = int(self.values[0])
                view = HookAdjustView(self.view.parent_view, hook_num)
                await select_interaction.response.send_message(
                    f"Adjusting Hook {hook_num}", view=view, ephemeral=True
                )

        class HookSelectView(discord.ui.View):
            def __init__(self, parent_view):
                super().__init__(timeout=30)
                self.parent_view = parent_view
                self.add_item(HookSelect())

        await interaction.response.send_message(
            "Select a Hook to adjust:", 
            view=HookSelectView(self), 
            ephemeral=True
        )

    async def pathos_plus(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Divine_Agony FROM Exorcists WHERE CID = ?", (self.cid,))
            result = cursor.fetchone()
            if result is None:
                await interaction.response.send_message("Character not found.", ephemeral=True)
                return
            current_pathos = int(result[0])  
            if current_pathos < 3:
                new_pathos = current_pathos + 1
                cursor.execute("UPDATE Exorcists SET Divine_Agony = ? WHERE CID = ?", (new_pathos, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, new_pathos)

    async def burn_pathos(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT Divine_Agony FROM Exorcists WHERE CID = ?", (self.cid,))
            result = cursor.fetchone()
            if result is None:
                await interaction.response.send_message("Character not found.", ephemeral=True)
                return
            new_pathos = 0
            cursor.execute("UPDATE Exorcists SET Divine_Agony = ? WHERE CID = ?", (new_pathos, self.cid))
            connection.commit()
            await self.refresh_embeds(interaction, new_pathos)

    async def gain_xp(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT XP, Advancements, ADD_BLSPH FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_xp = int(result[0])
                current_adv = int(result[1])
                add_blsph = int(result[2])
                new_xp = current_xp + 1
                if new_xp == 4 + add_blsph and current_adv < 3:
                    new_xp = 0
                    new_adv = current_adv + 1
                    cursor.execute("UPDATE Exorcists SET XP = ?, Advancements = ? WHERE CID = ?", (new_xp, new_adv, self.cid))
                if new_xp < 4 + add_blsph:
                    cursor.execute("UPDATE Exorcists SET XP = ? WHERE CID = ?", (new_xp, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, new_xp)
        except Exception as e:
            print(e)

    async def skill_menu(self, interaction: discord.Interaction):
        class SkillSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Force", value="Force"),
                    discord.SelectOption(label="Conditioning", value="Conditioning"),
                    discord.SelectOption(label="Coordination", value="Coordination"),
                    discord.SelectOption(label="Covert", value="Covert"),
                    discord.SelectOption(label="Interfacing", value="Interfacing"),
                    discord.SelectOption(label="Investigation", value="Investigation"),
                    discord.SelectOption(label="Surveillance", value="Surveillance"),
                    discord.SelectOption(label="Negotiation", value="Negotiation"),
                    discord.SelectOption(label="Authority", value="Authority"),
                    discord.SelectOption(label="Connection", value="Connection"),
                ]
                super().__init__(placeholder="Select a skill to increase...", options=options)

            async def callback(self, select_interaction: discord.Interaction):
                skill = self.values[0]
                view = SkillAdjustView(self.view.parent_view, skill)
                await select_interaction.response.send_message(
                    f"Adjusting {skill}", view=view, ephemeral=True
                )

        class SkillSelectView(discord.ui.View):
            def __init__(self, parent_view):
                super().__init__(timeout=30)
                self.parent_view = parent_view
                self.add_item(SkillSelect())

        await interaction.response.send_message(
            "Select a Skill to increase:", 
            view=SkillSelectView(self), 
            ephemeral=True
        )

    async def show_afflictions(self, interaction: discord.Interaction):
        print(f"afflictions is: {Afflictions}")
        try:
            modal = Afflictions(parent_view=self)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"Error in afflictions: {e}")

    async def show_gear(self, interaction: discord.Interaction):
        try:
            modal = Registered_Kit(parent_view=self)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"Error in kit: {e}")

    async def show_powers(self, interaction: discord.Interaction):
        try:
            modal = Update_powers(parent_view=self)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"Error in Powers: {e}")

    async def sin_overflow(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Total_Sin_Marks FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                current_sin_marks = int(result[0])
                new_sin_marks = current_sin_marks + 1
                new_sin = 0
                cursor.execute("UPDATE Exorcists SET Total_Sin_Marks = ?, Sin = ? WHERE CID = ?", (new_sin_marks, new_sin, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, new_sin)
        except Exception as e:
            print(e)

    async def cat_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Cat_Rating FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_cat = int(result[0])
                if current_cat < 7:  # Assuming max CAT is 7
                    new_cat = current_cat + 1
                    cursor.execute("UPDATE Exorcists SET Cat_Rating = ? WHERE CID = ?", (new_cat, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)  # Refresh with current stress
        except Exception as e:
            print(f"CAT increase error: {e}")

    async def psyche_minus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Psyche FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_psyche = int(result[0])
                if current_psyche > 0:
                    new_psyche = current_psyche - 1
                    cursor.execute("UPDATE Exorcists SET Psyche = ? WHERE CID = ?", (new_psyche, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Psyche decrease error: {e}")




    async def psyche_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Psyche, Cat_Rating FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_psyche = int(result[0])
                crating = int(result[1])
                max_psyche = math.ceil(2 + (crating / 2))

                if current_psyche < max_psyche:
                    new_psyche = current_psyche + 1
                    cursor.execute("UPDATE Exorcists SET Psyche = ? WHERE CID = ?", (new_psyche, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Psyche decrease error: {e}")



    async def burst_minus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Burst FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_burst = int(result[0])
                if current_burst > 0:
                    new_burst = current_burst - 1
                    cursor.execute("UPDATE Exorcists SET Burst = ? WHERE CID = ?", (new_burst, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Burst decrease error: {e}")




    async def burst_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Burst FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_burst = int(result[0])
                if current_burst < 3:
                    new_burst = current_burst + 1
                    cursor.execute("UPDATE Exorcists SET Burst = ? WHERE CID = ?", (new_burst, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Burst decrease error: {e}")






    async def kit_minus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Kit_Points FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_kpoints = int(result[0])
                if current_kpoints > 0:
                    new_kpoints = current_kpoints - 1
                    cursor.execute("UPDATE Exorcists SET Kit_Points = ? WHERE CID = ?", (new_kpoints, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Kit decrease error: {e}")




    async def kit_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Kit_Points, Kit_Mod FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_kpoints = int(result[0])
                kit_mod = int(result[1])

                if current_kpoints < (7 + kit_mod):
                    new_kpoints = current_kpoints + 1
                    cursor.execute("UPDATE Exorcists SET Kit_Points = ? WHERE CID = ?", (new_kpoints, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Kit increase error: {e}")



    async def scrip_minus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Scrip FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_scrip = int(result[0])
                new_scrip = current_scrip - 1
                cursor.execute("UPDATE Exorcists SET Scrip = ? WHERE CID = ?", (new_scrip, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Scrip decrease error: {e}")




    async def scrip_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Scrip FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_scrip = int(result[0])
                new_scrip = current_scrip + 1
                cursor.execute("UPDATE Exorcists SET Scrip = ? WHERE CID = ?", (new_scrip, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"scrip increase error: {e}")
    



    async def visitation_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Visitation, Scrip FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_visitation = int(result[0])
                current_scrip = int(result[1])

                if current_scrip >= 12 and current_visitation == 0:
                    new_visitation = current_visitation + 1
                    new_scrip = current_scrip - 12
                    cursor.execute("UPDATE Exorcists SET Visitation = ?, Scrip = ? WHERE CID = ?", (new_visitation, new_scrip, self.cid))
                    connection.commit()
                    await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"visitation increase error: {e}")

    async def kitmod_plus(self, interaction: discord.Interaction):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Kit_Mod FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return
                current_kmod = int(result[0])
                new_kmod = current_kmod + 1
                cursor.execute("UPDATE Exorcists SET Kit_Mod = ? WHERE CID = ?", (new_kmod, self.cid))
                connection.commit()
                await self.refresh_embeds(interaction, self.stress)
        except Exception as e:
            print(f"Kit increase error: {e}")




    async def previous(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.setup_buttons()  # Rebuild buttons for the new page
            await self.update_message(interaction)

    async def next(self, interaction: discord.Interaction):
        if self.current_page < len(self.embeds) - 1:
            try:
                self.current_page += 1
                self.setup_buttons()  # Rebuild buttons for the new page
                await self.update_message(interaction)
            except Exception as e:
                print(e)

    async def update_message(self, interaction: discord.Interaction):
        embed = self.embeds[self.current_page]
        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.embeds)}")
        await interaction.response.edit_message(embed=embed, view=self)

    async def refresh_embeds(self, interaction: discord.Interaction, new_stress: int):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Force, Conditioning, Coordination, Covert, Interfacing, "
                               "Investigation, Surveillance, Negotiation, Authority, Connection, Improvements, "
                               "Stress, Injuries, Sin, Total_Sin_Marks, HOOK1, HOOK2, HOOK3, Afflictions, Divine_Agony, XP, Advancements, Add_BLSPH, "
                               "Cat_Rating, Burst, Psyche, Kit_Points, Kit_Mod, Kit_Items, Agenda, Agenda_Items, Agenda_Abilities, Scrip, Blastphemy, "
                               "Sin_Marks, Observed_Power0, Observed_Power1, Observed_Power2, Observed_Power3, "
                               "Observed_Power4, HOOK1_NAME, HOOK2_NAME, HOOK3_NAME, Visitation, Q1, Q2, Q3, Q4, Q5 FROM Exorcists WHERE CID = ?", (self.cid,))
                result = cursor.fetchone()
                if result is None:
                    await interaction.response.send_message("Character not found.", ephemeral=True)
                    return

                self.force = int(result[0] or 0)
                self.conditioning = int(result[1] or 0)
                self.coordination = int(result[2] or 0)
                self.covert = int(result[3] or 0)
                self.interfacing = int(result[4] or 0)
                self.investigation = int(result[5] or 0)
                self.surveillance = int(result[6] or 0)
                self.negotiation = int(result[7] or 0)
                self.authority = int(result[8] or 0)
                self.con = int(result[9] or 0)
                self.improvemments = int(result[10] or 0)
                self.stress = int(result[11] or 0)
                self.injuries = int(result[12] or 0)
                self.sin = int(result[13] or 0)
                self.total_sin_marks = int(result[14] or 0)
                self.hook1 = int(result[15] or 0)
                self.hook2 = int(result[16] or 0)
                self.hook3 = int(result[17] or 0)
                self.afflictions = result[18] or "None"
                self.pathos = int(result[19] or 0)
                self.xp = int(result[20] or 0)
                self.advances = int(result[21] or 0)
                add_blsph = int(result[22] or 0)
                self.crating = int(result[23] or 0)
                self.burst = int(result[24] or 0)
                self.psyche = int(result[25] or 0)
                self.kpoints = int(result[26] or 0)
                self.kmod = int(result[27] or 0)
                self.kitems = result[28] or "None"
                self.agenda = result[29] or "None"
                self.aitems = result[30] or "None"
                self.aabilities = result[31] or "None"
                self.scrip = result[32] or 0
                self.blsph = result[33] or "None"
                self.sin_marks = result[34] or 0
                self.power0 = result[35] or "None"
                self.power1 = result[36] or "None"
                self.power2 = result[37] or "None"
                self.power3 = result[38] or "None"
                self.power4 = result[39] or "None"
                self.hook1_name = result[40]
                self.hook2_name = result[41]
                self.hook3_name = result[42]
                self.visrights = result[43]
                self.q1 = result[44]
                self.q2 = result[45]
                self.q3 = result[46]
                self.q4 = result[47]
                self.q5 = result[48]
                self.max_stress = 6 - self.injuries
                self.max_kit = 7 + self.kmod
                self.max_psyche = math.ceil(2 + (self.crating / 2))

            # Update all embeds based on current page
            def get_skill_boxes(value, max_boxes=3):
                filled = "■" * value
                empty = "□" * (max_boxes - value)
                return f"{filled} {empty}".strip()

            def get_stress_boxes(value, max_boxes=6):
                filled = "■" * value
                empty = "□" * (max_boxes - value - self.injuries)
                return f"{filled} {empty}".strip()

            def get_imp_boxes(value, max_boxes=6):
                filled = "■" * value
                empty = "□" * (max_boxes - value)
                return f"{filled} {empty}".strip()

            def get_sin_boxes(value, max_boxes=10):
                filled = "■" * value
                empty = "□" * (max_boxes - value - self.total_sin_marks)
                return f"{filled} {empty}".strip()

            def get_hook_boxes(value, max_boxes=3):
                filled = "■" * value
                empty = "□" * (max_boxes - value)
                return "\n".join(filled + empty)

            def get_xp_boxes(value, max_boxes=4 + add_blsph):
                filled = "■" * value
                empty = "□" * (max_boxes - value)
                return f"{filled} {empty}".strip()

            def get_pathos_boxes(value, max_boxes=3):
                filled = "★" * value
                empty = "☆" * (max_boxes - value)
                return f"{filled} {empty}".strip()

            def get_cat_boxes(value, max_boxes=7):
                filled = "▲" * value
                empty = "△" * (max_boxes - value)
                return f"{filled} {empty}".strip()

            def get_psyche_boxes(value, max_boxes=self.max_psyche):
                filled = "■" * value
                empty = "□" * (max_boxes - value)
                return f"{filled} {empty}".strip()

            def get_kit_boxes(value, max_boxes=self.max_kit):
                filled = "■" * value
                empty = "□" * (max_boxes - value)
                return f"{filled} {empty}".strip()

            # Update page 1
            self.embeds[0].clear_fields()
            self.embeds[0].add_field(name="", value=(
                f"**Max stress:** {self.max_stress} {get_stress_boxes(self.stress)}\n"
                f"**Total Injuries:** {get_skill_boxes(self.injuries)}\n"
                f"**Current Sin:** {get_sin_boxes(self.sin)}\n"
                f"**Sin Marks:** {self.total_sin_marks}\n"
                f'**{self.hook1_name}:**\n {get_hook_boxes(self.hook1)}\n'
                f'**{self.hook2_name}:**\n {get_hook_boxes(self.hook2)}\n'
                f'**{self.hook3_name}:**\n {get_hook_boxes(self.hook3)}\n'
                f'**Afflictions:**\n {self.afflictions}\n'
            ))
            self.embeds[0].add_field(name="Registered Skills: ", value=(
                f"**Force:** {get_skill_boxes(self.force)}\n"
                f"**Conditioning:** {get_skill_boxes(self.conditioning)}\n"
                f"**Coordination:** {get_skill_boxes(self.coordination)}\n"
                f"**Covert:** {get_skill_boxes(self.covert)}\n"
                f"**Interfacing:** {get_skill_boxes(self.interfacing)}\n"
                f"**Investigation:** {get_skill_boxes(self.investigation)}\n"
                f"**Surveillance:** {get_skill_boxes(self.surveillance)}\n"
                f"**Negotiation:** {get_skill_boxes(self.negotiation)}\n"
                f"**Authority:** {get_skill_boxes(self.authority)}\n"
                f"**Connection:** {get_skill_boxes(self.con)}\n"
                f"**Improvements:** {get_imp_boxes(self.improvemments)}\n"
                f"**Pathos:** {get_pathos_boxes(self.pathos)}\n"
                f"**XP:** {get_xp_boxes(self.xp)}\n"
                f"**Advancements:**\n {get_skill_boxes(self.advances)}\n"
            ))

            # Update page 2
            self.embeds[1].clear_fields()
            self.embeds[1].add_field(name="", value=(
                f"**CAT:** {get_cat_boxes(self.crating)}\n"
                f"**Psyche:** {get_psyche_boxes(self.psyche)}\n"
                f"**Burst:** {get_skill_boxes(self.burst)}\n"
                f"**Kit Points:** {get_kit_boxes(self.kpoints)}\n"
                f"**Current Kit:**\n {self.kitems}\n"
                f"**Scrip:** {self.scrip}\n"
                f"**Sin Marks:**\n {self.sin_marks}\n"
            ))
            self.embeds[1].add_field(name="AGNDA: ", value=(
                f"**AGENDA:** {self.agenda}\n"
                f"**Agenda Items:**\n {self.aitems}\n"
                f"**Agenda Abilities:**\n {self.aabilities}\n"
            ))

            # Update page 3
            self.embeds[2].clear_fields()
            self.embeds[2].add_field(name="", value=f"**Observed Power:** {self.power0}\n", inline=False)
            self.embeds[2].add_field(name="", value=f"**Observed Power:** {self.power1}\n", inline=False)
            self.embeds[2].add_field(name="", value=f"**Observed Power:** {self.power2}\n", inline=True)
            self.embeds[2].add_field(name="", value=f"**Observed Power:** {self.power3}\n", inline=True)
            self.embeds[2].add_field(name="", value=f"**Observed Power:** {self.power4}\n", inline=True)

            # Update page 4
            self.embeds[3].clear_fields()
            self.embeds[3].add_field(name="Onboarding Questions: ", value=(
                    f"**When Did Your Powers First Develop?:** {self.q1}\n"
                    f"**Is your sin-seed in your brain or in your heart?**\n {self.q2}\n"
                    f"**What do you hide in the deepest parts of you?** {self.q3}\n"
                    f"**Is your hand your hand?** {self.q4}\n"
                    f"**Do you remember the face of your mother?** {self.q5}\n"

                ))
            # Update page 5
            self.embeds[4].clear_fields()
            self.embeds[4].add_field(name="Misc info: ", 
                        value=(f"**Kit Point Modifier:** {self.kmod}\n"
                        f"**Visitation Rights:**\n {self.visrights}\n"
                        f"**Scrip:** {self.scrip}\n"))


            

            

            self.setup_buttons()  # Rebuild buttons after refresh
            await self.update_message(interaction)
        except ValueError as e:
            await interaction.response.send_message(f"Error converting data: {e}", ephemeral=True)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)



class ViewSheet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./config/db/Exorcists.db"



    @app_commands.command(name="view_sheet", description="Display Character Sheet")
    async def view_sheet(self, interaction: discord.Interaction, cid: str):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT Force, Conditioning, Coordination, Covert, Interfacing, "
                               "Investigation, Surveillance, Negotiation, Authority, Connection, Improvements, "
                               "Stress, Injuries, Sin, Total_Sin_Marks, HOOK1, HOOK2, HOOK3, Afflictions, Divine_Agony, XP, Advancements, Add_BLSPH, "
                               "Cat_Rating, Burst, Psyche, Kit_Points, Kit_Mod, Kit_Items, Agenda, Agenda_Items, Agenda_Abilities, Scrip, Blastphemy, "
                               "Sin_Marks, Observed_Power0, Observed_Power1, Observed_Power2, Observed_Power3, "
                               "Observed_Power4, HOOK1_NAME, HOOK2_NAME, HOOK3_NAME, Visitation, Q1, Q2, Q3, Q4, Q5 FROM Exorcists WHERE CID = ?", (cid,))
                result = cursor.fetchone()

                if not result:
                    await interaction.response.send_message(f"No character found with CID: {cid}", ephemeral=True)
                    return



                self.force = int(result[0] or 0)
                self.conditioning = int(result[1] or 0)
                self.coordination = int(result[2] or 0)
                self.covert = int(result[3] or 0)
                self.interfacing = int(result[4] or 0)
                self.investigation = int(result[5] or 0)
                self.surveillance = int(result[6] or 0)
                self.negotiation = int(result[7] or 0)
                self.authority = int(result[8] or 0)
                self.con = int(result[9] or 0)
                self.improvemments = int(result[10] or 0)
                self.stress = int(result[11] or 0)
                self.injuries = int(result[12] or 0)
                self.sin = int(result[13] or 0)
                self.total_sin_marks = int(result[14] or 0)
                self.hook1 = int(result[15] or 0)
                self.hook2 = int(result[16] or 0)
                self.hook3 = int(result[17] or 0)
                self.afflictions = result[18] or "None"
                self.pathos = int(result[19] or 0)
                self.xp = int(result[20] or 0)
                self.advances = int(result[21] or 0)
                add_blsph = int(result[22] or 0)
                self.crating = int(result[23] or 0)
                self.burst = int(result[24] or 0)
                self.psyche = int(result[25] or 0)
                self.kpoints = int(result[26] or 0)
                self.kmod = int(result[27] or 0)
                self.kitems = result[28] or "None"
                self.agenda = result[29] or "None"
                self.aitems = result[30] or "None"
                self.aabilities = result[31] or "None"
                self.scrip = result[32] or 0
                self.blsph = result[33] or "None"
                self.sin_marks = result[34] or 0
                self.power0 = result[35] or "None"
                self.power1 = result[36] or "None"
                self.power2 = result[37] or "None"
                self.power3 = result[38] or "None"
                self.power4 = result[39] or "None"
                self.hook1_name = result[40]
                self.hook2_name = result[41]
                self.hook3_name = result[42]
                self.visrights = result[43]
                self.q1 = result[44]
                self.q2 = result[45]
                self.q3 = result[46]
                self.q4 = result[47]
                self.q5 = result[48]
                self.max_stress = 6 - self.injuries
                self.max_kit = 7 + self.kmod
                self.max_psyche = math.ceil(2 + (self.crating / 2))



                def get_skill_boxes(value, max_boxes=3):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value)
                    return f"{filled} {empty}".strip()



                def get_stress_boxes(value, max_boxes=6):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value - self.injuries)
                    return f"{filled} {empty}".strip()



                def get_imp_boxes(value, max_boxes=6):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value)
                    return f"{filled} {empty}".strip()



                def get_sin_boxes(value, max_boxes=10):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value - self.total_sin_marks - add_blsph)
                    return f"{filled} {empty}".strip()



                def get_hook_boxes(value, max_boxes=3):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value)
                    return "\n".join(filled + empty)



                def get_xp_boxes(value, max_boxes=4 + add_blsph):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value)
                    return f"{filled} {empty}".strip()



                def get_pathos_boxes(value, max_boxes=3):
                    filled = "★" * value
                    empty = "☆" * (max_boxes - value)
                    return f"{filled} {empty}".strip()



                def get_cat_boxes(value, max_boxes=7):
                    filled = "▲" * value
                    empty = "△" * (max_boxes - value)
                    return f"{filled} {empty}".strip()



                def get_psyche_boxes(value, max_boxes=self.max_psyche):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value)
                    return f"{filled} {empty}".strip()


                def get_kit_boxes(value, max_boxes=self.max_kit):
                    filled = "■" * value
                    empty = "□" * (max_boxes - value)
                    return f"{filled} {empty}".strip()
                embeds = []



                sheet_embed1 = discord.Embed(title=f'Information Regarding Exorcist {cid}', color=discord.Color.blue())
                file = discord.File(f"./config/images/{cid}.png", filename="image.png")
                sheet_embed1.set_image(url="attachment://image.png")
                sheet_embed1.add_field(name="", value=(
                    f"**Max stress:** {self.max_stress} {get_stress_boxes(self.stress)}\n"
                    f"**Total Injuries:** {get_skill_boxes(self.injuries)}\n"
                    f"**Current Sin:** {get_sin_boxes(self.sin)}\n"
                    f"**Sin Marks:** {self.total_sin_marks}\n"
                    f'**{self.hook1_name}:**\n {get_hook_boxes(self.hook1)}\n'
                    f'**{self.hook2_name}:**\n {get_hook_boxes(self.hook2)}\n'
                    f'**{self.hook2_name}:**\n {get_hook_boxes(self.hook3)}\n'
                    f'**Afflictions:**\n {self.afflictions}\n'

                ))

                sheet_embed1.add_field(name="Registered Skills: ", value=(
                    f"**Force:** {get_skill_boxes(self.force)}\n"
                    f"**Conditioning:** {get_skill_boxes(self.conditioning)}\n"
                    f"**Coordination:** {get_skill_boxes(self.coordination)}\n"
                    f"**Covert:** {get_skill_boxes(self.covert)}\n"
                    f"**Interfacing:** {get_skill_boxes(self.interfacing)}\n"
                    f"**Investigation:** {get_skill_boxes(self.investigation)}\n"
                    f"**Surveillance:** {get_skill_boxes(self.surveillance)}\n"
                    f"**Negotiation:** {get_skill_boxes(self.negotiation)}\n"
                    f"**Authority:** {get_skill_boxes(self.authority)}\n"
                    f"**Connection:** {get_skill_boxes(self.con)}\n"
                    f"**Improvements:** {get_imp_boxes(self.improvemments)}\n"
                    f"**Pathos:** {get_pathos_boxes(self.pathos)}\n"
                    f"**XP:** {get_xp_boxes(self.xp)}\n"
                    f"**Advancements:**\n {get_skill_boxes(self.advances)}\n"

                ))

                embeds.append(sheet_embed1)



                sheet_embed2 = discord.Embed(title=f'Information Regarding Exorcist {cid}', color=discord.Color.blue())
                file = discord.File(f"./config/images/{cid}.png", filename="image.png")
                sheet_embed2.set_image(url="attachment://image.png")

                sheet_embed2.add_field(name="", value=(
                    f"**CAT:** {get_cat_boxes(self.crating)}\n"
                    f"**Psyche:** {get_psyche_boxes(self.psyche)}\n"
                    f"**Burst:** {get_skill_boxes(self.burst)}\n"
                    f"**Kit Points:** {get_kit_boxes(self.kpoints)}\n"
                    f"**Current Kit:**\n {self.kitems}\n"
                    f"**Sin Marks:**\n {self.sin_marks}\n"

                ))

                sheet_embed2.add_field(name="AGNDA: ", value=(
                    f"**AGENDA:** {self.agenda}\n"
                    f"**Agenda Items:**\n {self.aitems}\n"
                    f"**Agenda Abilities:**\n {self.aabilities}\n"

                ))

                embeds.append(sheet_embed2)
                sheet_embed3 = discord.Embed(title=f'Information Regarding Exorcist {cid}', color=discord.Color.blue())
                file = discord.File(f"./config/images/{cid}.png", filename="image.png")
                sheet_embed3.set_image(url="attachment://image.png")
                sheet_embed3.add_field(name="", value=f"**Observed Power:** {self.power0}\n", inline=False)
                sheet_embed3.add_field(name="", value=f"**Observed Power:** {self.power1}\n", inline=False)
                sheet_embed3.add_field(name="", value=f"**Observed Power:** {self.power2}\n", inline=True)
                sheet_embed3.add_field(name="", value=f"**Observed Power:** {self.power3}\n", inline=True)
                sheet_embed3.add_field(name="", value=f"**Observed Power:** {self.power4}\n", inline=True)
                embeds.append(sheet_embed3)

                sheet_embed4 = discord.Embed(title=f'Information Regarding Exorcist {cid}', color=discord.Color.blue())
                file = discord.File(f"./config/images/{cid}.png", filename="image.png")
                sheet_embed4.set_image(url="attachment://image.png")
                sheet_embed4.add_field(name="Onboarding Questions: ", value=(
                    f"**When Did Your Powers First Develop?:** {self.q1}\n"
                    f"**Is your sin-seed in your brain or in your heart?**\n {self.q2}\n"
                    f"**What do you hide in the deepest parts of you?** {self.q3}\n"
                    f"**Is your hand your hand?** {self.q4}\n"
                    f"**Do you remember the face of your mother?** {self.q5}\n"

                ))
                
                embeds.append(sheet_embed4)


                sheet_embed5 = discord.Embed(title=f'Information Regarding Exorcist {cid}', color=discord.Color.blue())
                file = discord.File(f"./config/images/{cid}.png", filename="image.png")
                sheet_embed5.set_image(url="attachment://image.png")
                sheet_embed5.add_field(name="Misc info: ", value=(
                    f"**Kit Point Modifier:** {self.kmod}\n"
                    f"**Visitation Rights:**\n {self.visrights}\n"
                    f"**Scrip:** {self.scrip}\n"

                ))
                
                embeds.append(sheet_embed5)
                view = SheetView(embeds, interaction, cid, self.db_path)
                view.message = await interaction.user.send(file=file, embed=embeds[0].set_footer(text="Page 1 of 5"), view=view)

        except Exception as e:
            print(e)
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            await interaction.response.defer()

async def setup(bot):
    await bot.add_cog(ViewSheet(bot), guilds=[GUILD_ID])