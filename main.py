import requests, os
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF


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

    # Invalid artist search check
    if artist_name.lower() not in artist["name"].lower():
        print("No exact match found, try again.\n")
        continue

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

    choice1 = input("Would you like to see their top tracks? (y/n): ")

    if choice1 == "y":
        top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
        response = requests.get(top_tracks_url, headers=headers, params={"Market": "US"})
        tracks = response.json()["tracks"]

        # Create table of top track stats
        rows = []
        for track in tracks:
            rows.append({
                "Track": track["name"],
                "Album": track["album"]["name"],
                "Popularity": track["popularity"],
                "Duration": track["duration_ms"] // 60000
            })
        df = pd.DataFrame(rows)

        # Create PDF of stats table
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Top Tracks for {artist_name}", ln=True, align="C")

        # Table header
        pdf.set_font("Arial", size=10)
        pdf.cell(60, 10, "Track", border=1)
        pdf.cell(60, 10, "Album", border=1)
        pdf.cell(30, 10, "Popularity", border=1)
        pdf.cell(30, 10, "Duration", border=1, ln=True)

        # Table rows
        for _, row in df.iterrows():
            pdf.cell(60, 10, row["Track"][:30], border=1)  # [:30] trims long names
            pdf.cell(60, 10, row["Album"][:30], border=1)
            pdf.cell(30, 10, str(row["Popularity"]), border=1)
            pdf.cell(30, 10, str(row["Duration"]) + " min", border=1, ln=True)

        # loop through df rows and add to PDF table
        pdf.output(f"top_tracks_{artist_name}.pdf")

    choice2 = input("Search for another artist? (y/n): ")
    print("")

    if choice2 == "n":
        break

