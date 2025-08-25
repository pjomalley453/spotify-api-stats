import requests, os
from dotenv import load_dotenv

# Load secrets
load_dotenv()  # load from .env
client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

# Token function
def get_spotify_token():
    token_url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    resp = requests.post(token_url, data=data, auth=(client_id, client_secret))

    # print("Status:", resp.status_code)
    # print("Text:", resp.text)

    token_json = resp.json()
    return token_json["access_token"]

# Get fresh token
access_token = get_spotify_token()
headers = {"Authorization": f"Bearer {access_token}"}

# ARTIST SEARCH
while True:
    artist_name = input("Enter an artist name: ").lower()
    print("")
    search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    params = {"q": artist_name, "type": "artist", "limit": 1}

    search_response = requests.get(search_url, headers=headers, params=params)
    artist_data = search_response.json()
    # print(artist_data)

    # Extract Fields
    artist = artist_data["artists"]["items"][0]

    artist_id = artist["id"]
    artist_name = artist["name"]
    artist_url = artist["external_urls"]["spotify"]
    artist_genres = artist["genres"]
    artist_followers = artist["followers"]["total"]

    # Print results
    print("🎵 Artist:", artist_name)
    print("👥 Followers:", artist_followers)

    print("💿 Genres:", ", ".join(artist_genres))
    print("")
    # print("🆔 ID:", artist_id)
    print("🔗 URL:", artist_url)
    print("")

    choice = input("Search for another artist? (y/n): ")
    print("")

    if choice == "n":
        break

