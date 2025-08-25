import requests, os
from dotenv import load_dotenv

load_dotenv()  # load from .env

client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

def get_spotify_token():
    token_url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    resp = requests.post(token_url, data=data, auth=(client_id, client_secret))
    token_json = resp.json()
    return token_json["access_token"]

access_token = get_spotify_token()
headers = {"Authorization": f"Bearer {access_token}"}

