import pygame
import discord
from discord.ext import commands
from discord import app_commands
from main import GUILD_ID  
import random
import math
from PIL import Image
import os
import traceback

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

WIDTH, HEIGHT = 400, 400
WHITE = (105, 105, 105)
BLACK = (0, 0, 0)
COLOURS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
center = (WIDTH // 2, HEIGHT // 2)
radius = 150
spin_speed = 15
deceleration = 0.2

def draw_wheel(angle, screen, names, draw_pointer=True):
    screen.fill(WHITE)
    num_sections = len(names)
    angle_per_section = 360 / num_sections
    
    for i in range(num_sections):
        section_points = []
        num_points = 60
        start_angle = math.radians(angle + i * angle_per_section)
        end_angle = math.radians(angle + (i + 1) * angle_per_section)
        
        section_points.append(center)
        for j in range(num_points + 1):
            theta = start_angle + (end_angle - start_angle) * j / num_points
            x = center[0] + radius * math.cos(theta)
            y = center[1] + radius * math.sin(theta)
            section_points.append((x, y))
        
        pygame.draw.polygon(screen, COLOURS[i % len(COLOURS)], section_points)

        font = pygame.font.SysFont(None, 24)
        max_text_length = 16
        display_name = names[i]
        if len(display_name) > max_text_length:
            display_name = display_name[:max_text_length-3] + '...'
        
        text = font.render(display_name, True, BLACK)  
        mid_angle = start_angle + (end_angle - start_angle) / 2
        text_surface = pygame.transform.rotate(text, -(math.degrees(mid_angle)))
        text_rect = text_surface.get_rect(center=(
            center[0] + (radius * 0.5) * math.cos(mid_angle),
            center[1] + (radius * 0.5) * math.sin(mid_angle)

        
        ))
        screen.blit(text_surface, text_rect)

    if draw_pointer:
        pointer_base_width = 20
        pointer_height = 30
        pointer_points = [
            (center[0] - pointer_base_width // 2, center[1] - radius - 10),  
            (center[0] + pointer_base_width // 2, center[1] - radius - 10), 
            (center[0], center[1] - radius + pointer_height)  
        ]
        pygame.draw.polygon(screen, BLACK, pointer_points)

def generate_gif(names):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wheel of Names")

    angle = random.uniform(0, 360)
    current_speed = spin_speed + random.uniform(-2, 2)
    frames = []
    frame_count = 0

    if not os.path.exists("frames"):
        os.makedirs("frames")

    try:
        while current_speed > 0 or frame_count < 20:
            draw_wheel(angle, screen, names)
            pygame.display.flip()

            frame_path = f'frames/frame_{frame_count:03d}.png'
            pygame.image.save(screen, frame_path)
            frames.append(Image.open(frame_path))

            angle += current_speed
            current_speed -= deceleration
            if current_speed < 0:
                current_speed = 0
            frame_count += 1

        final_angle = (angle + 90) % 360
        winner_index = int(final_angle // (360 / len(names)))
        winner = names[len(names) - 1 - winner_index]
        print(f'Winner: {winner}')

        for _ in range(10):
            draw_wheel(angle, screen, names)
            pygame.display.flip()
            frame_path = f'frames/frame_{frame_count:03d}.png'
            pygame.image.save(screen, frame_path)
            frames.append(Image.open(frame_path))
            frame_count += 1

        gif_path = "wheel_of_names.gif"
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=50,
            loop=0
        )

        for i in range(frame_count):
            os.remove(f"frames/frame_{i:03d}.png")
        os.rmdir("frames")

        print("GIF saved as 'wheel_of_names.gif'")
        return winner, gif_path

    except Exception as e:
        print(f"Error generating GIF: {e}")
        traceback.print_exc()
        raise  
    finally:
        pygame.quit()  

class Wheel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name="spin", description="Spin a wheel with custom names!")
    @app_commands.describe(names="Enter names separated by commas (e.g., Alice, Bob, Charlie)")
    async def spin(self, interaction: discord.Interaction, names: str):
        await interaction.response.defer()

        name_list = [name.strip() for name in names.split(',') if name.strip()]
        if not name_list:
            await interaction.followup.send("Please provide at least one name!")
            return
        if len(name_list) < 2:
            await interaction.followup.send("Please provide at least two names to spin the wheel!")
            return

        try:
            winner, gif_path = generate_gif(name_list)
            with open(gif_path, "rb") as f:
                file = discord.File(f, "wheel_of_names.gif")
                await interaction.followup.send(f"The wheel has spoken! Winner: {winner}", file=file)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            print(f"Command error: {e}")
            traceback.print_exc()

async def setup(bot):
    await bot.add_cog(Wheel(bot), guilds=[GUILD_ID])