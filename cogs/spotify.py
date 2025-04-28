from discord.ext import commands
import requests
import base64
import json
import re
import os
from main import GUILD_ID
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"

class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def refresh_access_token(self):
        try:
            
            client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
            client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
            headers = {
                "Authorization": f"Basic {client_creds_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "refresh_token",
                "refresh_token": REFRESH_TOKEN
            }
            response = requests.post(TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("No access token received")
            print("Access token refreshed successfully")
            return access_token
        except requests.RequestException as e:
            print(f"Error refreshing access token: {e}")
            raise
        except ValueError as e:
            print(f"Token refresh failed: {e}")
            raise

    def get_user_id(self, access_token):
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{API_BASE_URL}/me", headers=headers)
            response.raise_for_status()
            user_data = response.json()
            user_id = user_data.get("id")
            print(f"Retrieved user ID: {user_id}")
            return user_id
        except requests.RequestException as e:
            print(f"Error fetching user ID: {e}")
            raise

    def create_playlist(self, access_token, user_id, name="Groove Grove", description="Groove Grove"):
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                f"{API_BASE_URL}/users/{user_id}/playlists",
                headers=headers,
                params={"limit": 50}
            )
            response.raise_for_status()
            playlists = response.json().get("items", [])
            for playlist in playlists:
                if playlist["name"] == name:
                    print(f"Found existing playlist: {name}")
                    return playlist["id"]
            data = {
                "name": name,
                "description": description,
                "public": False
            }
            response = requests.post(
                f"{API_BASE_URL}/users/{user_id}/playlists",
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            playlist_id = response.json().get("id")
            print(f"Created new playlist: {name} (ID: {playlist_id})")
            return playlist_id
        except requests.RequestException as e:
            print(f"Error creating/finding playlist: {e}")
            raise

    def parse_spotify_url(self, url):
        pattern = r"https?://open\.spotify\.com/album/([a-zA-Z0-9]{22})"
        match = re.match(pattern, url)
        if not match:
            raise ValueError("Invalid Spotify album URL")
        return match.group(1)

    def get_album_tracks(self, access_token, album_id):
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            track_uris = []
            next_url = f"{API_BASE_URL}/albums/{album_id}/tracks?limit=50"
            
            while next_url:
                response = requests.get(next_url, headers=headers)
                print(f"Album Tracks Response Status: {response.status_code}")
                print(f"Album Tracks Response Text: {response.text}")
                response.raise_for_status()
                data = response.json()
                tracks = data.get("items", [])
                track_uris.extend([track["uri"] for track in tracks])
                next_url = data.get("next")
            
            print(f"Found {len(track_uris)} tracks for album ID: {album_id}")
            return track_uris
        except requests.RequestException as e:
            print(f"Error fetching album tracks: {e}")
            raise

    def add_tracks_to_playlist(self, access_token, playlist_id, track_uris):
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            data = {"uris": track_uris}
            response = requests.post(
                f"{API_BASE_URL}/playlists/{playlist_id}/tracks",
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            print(f"Added {len(track_uris)} tracks to playlist {playlist_id}")
        except requests.RequestException as e:
            print(f"Error adding tracks to playlist: {e}")
            raise

    
    async def add_album(self, url: str):
       
        try:
            access_token = self.refresh_access_token()
            user_id = self.get_user_id(access_token)
            playlist_id = self.create_playlist(access_token, user_id)
            album_id = self.parse_spotify_url(url)
            track_uris = self.get_album_tracks(access_token, album_id)
            if not track_uris:
                return
            self.add_tracks_to_playlist(access_token, playlist_id, track_uris)
        except ValueError as e:
            print(f"Error in add_album: {e}")
        except Exception as e:
            print(f"Error in add_album: {e}")

async def setup(bot):
    await bot.add_cog(Spotify(bot), guilds=[GUILD_ID])