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


def search_artist():
    while True:
        artist_name = input("Enter an artist name: ").lower()
        print("")

        search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
        params = {"q": artist_name, "type": "artist", "limit": 1}
        search_response = requests.get(search_url, headers=headers, params=params)
        artist_data = search_response.json()
        # print(artist_data)

        # Invalid artist search check
        if not artist_data["artists"]["items"]:  # no results
            print("No match found, try again.\n")
            continue

        # Extract first artist
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
        print("🔗 URL:", artist_url)
        print("")

        choice = input("Use this artist? (y/n): ")
        if choice.lower() == "y":
            return artist_id, artist_name


# TOP TRACK REPORT
def artist_track_report(artist_id, artist_name):
    top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    response = requests.get(top_tracks_url, headers=headers, params={"market": "US"})
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
    safe_name = artist_name.replace(" ", "_")
    pdf.output(f"top_tracks_{safe_name}.pdf")


def generate_comparison_report(searched_artists):

    rows = []

    for artist in searched_artists:
        artist_id = artist["id"]

        # Call Spotify API for artist profile
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        response = requests.get(url, headers=headers)
        data = response.json()

        # Extract fields
        name = data["name"]
        followers = data["followers"]["total"]
        popularity = data["popularity"]

        # Add to rows
        rows.append({
            "artist": name,
            "Followers:": followers,
            "Popularity": popularity
        })

    # Put rows into data DataFrame


def main():
    searched_artists = []
    search_counter = 0

    while True:
        # 1. Search for artist
        artist_id, artist_name = search_artist()
        search_counter += 1

        # 2. Generate artist's top tracks report?
        choice1 = input("Would you like to see their top tracks printed as a PDF? (y/n): ").lower()
        if choice1 == "y":
            artist_track_report(artist_id, artist_name)

        # 3. Add to saved searches list?
        choice2 = input("Add artist to saved searches? (y/n): ").lower()
        if choice2 == "y":
            searched_artists.append({"id": artist_id, "name": artist_name})

        # 4. Offer comparison of 2+ artists
        if search_counter >= 2:
            choice3 = input(f"Compare top tracks of your {search_counter} searched artists? (y/n): ").lower()
            if choice3 == "y":
                generate_comparison_report(searched_artists)
                break

        # search again?
        again = input("Search for another artist? (y/n): ")
        if again.lower() == "n":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()


##### MASTER PLAN #####

# searched_artists = []

# ask user to search for artist
# increment search_counter

# ask user if they want to generate PDF chart of top tracks' stats
# if y:
#   add artist to searched_artists list
#   parse track stats
#   create PDF / export
# if n:
#   if search_counter >= 2
#       ask user: "Create a PDF comparing top tracks of your searched artists?"
#   break

# continue while loop

# main_prompt = input("Enter an option (search/report) ")

# ARTIST SEARCH


# if search_counter >= 2:
#     search_choice = input(f"Search for an artist or compare top tracks of "
#                           f"{search_counter} searched artists? (artist/compare)").lower




