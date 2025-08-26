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
        print("👥 Followers:", f"{artist_followers:,}")
        if artist_genres:
            print("💿 Genres:", ", ".join(artist_genres))
        else:
            print("💿 Genres: N/A")
        print("")
        print("🔗 URL:", artist_url)
        print("")

        return artist_id, artist_name


def write_comparison_excel(df, path="artist_comparison.xlsx"):
    with pd.ExcelWriter(path, engine="xlsxwriter") as xw:
        df.to_excel(xw, sheet_name="Comparison", index=False)
        ws = xw.sheets["Comparison"]

        # Create formats
        header_fmt = xw.book.add_format({"bold": True})
        num_fmt = xw.book.add_format({"num_format": "#,##0"})

        # Apply header format (row 0)
        for col_idx, col_name in enumerate(df.columns): ws.write(0, col_idx, col_name, header_fmt)

        # Apply number format to Followers column (find its index)
        followers_col = list(df.columns).index("Followers")
        ws.set_column(followers_col, followers_col, 14, num_fmt)

        # Reasonable widths for other columns
        ws.set_column(0, 0, 22)  # Artist
        ws.set_column(2, 2, 11)  # Popularity
        ws.set_column(3, 3, 40)  # Genres

        # Freeze header row & add filter
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, len(df), len(df.columns)-1)

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

    # Create PDF of stats
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Top Tracks for {artist_name}", ln=True, align="C")

    # Table header
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(60, 10, "Track", border=1)
    pdf.cell(60, 10, "Album", border=1)
    pdf.cell(30, 10, "Popularity", border=1)
    pdf.cell(30, 10, "Duration", border=1, ln=True)

    # Table rows
    pdf.set_font("Arial", size=10)
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
        genres = data["genres"]

        # Add to rows
        rows.append({
            "Artist": name,
            "Followers": followers,
            "Popularity": popularity,
            "Genres": ", ".join([g.title() for g in genres])  if genres else "N/A"
        })

    # Put rows into data DataFrame
    df = pd.DataFrame(rows)

    # Ask to sort
    sort_field = input("Sort by (followers/popularity): ").strip().lower()
    if sort_field not in {"followers", "popularity"}:
        sort_field = "followers"  # default

    order = input("Order (asc/desc): ").strip().lower()
    ascending = (order == "asc")

    df = df.sort_values(by=sort_field.capitalize(), ascending=ascending)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Comparison of Searched Artists by {sort_field.title()}", ln=True, align="C")

    # Table header
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(50, 10, "Artist", border=1)
    pdf.cell(40, 10, "Followers", border=1)
    pdf.cell(30, 10, "Popularity", border=1)
    pdf.cell(70, 10, "Genres", border=1, ln=True)

    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(50, 10, row["Artist"][:20], border=1)
        pdf.cell(40, 10, f"{int(row['Followers']):,}", border=1)  # format here
        pdf.cell(30, 10, str(int(row["Popularity"])), border=1)
        pdf.cell(70, 10, row["Genres"][:35], border=1, ln=True)

    pdf.output("artist_comparison_report.pdf")


def main():
    searched_artists = []

    while True:
        print("")
        user_prompt = input("Choose an option: (search/report/saved/delete/quit) ").lower()

        # 1. Search for artist
        if user_prompt == "search":
            artist_id, artist_name = search_artist()

            # Add to saved searches
            choice1 = input("Add this artist to your saved searches? (y/n): ").lower()
            if choice1 == "y":
                if not any(a["id"] == artist_id for a in searched_artists):
                    searched_artists.append({"id": artist_id, "name": artist_name})
                    print(f"{artist_name} added to saved searches.\n")
                else:
                    print(f"{artist_name} is already in your saved searches.\n")

        # 2. Create report
        elif user_prompt == "report":
            report_choice = input("Create individual artist report or comparison report?: (1/2)")

            # Individual artist report
            if report_choice == "1":
                if not searched_artists:
                    print("No artists saved yet.")
                else:
                    for item in searched_artists:
                        print(item["name"])

                    name = input("Type the artist name: ").strip().lower()
                    match = next((a for a in searched_artists if a["name"].lower() == name), None)

                    if not match:
                        print("Artist not in saved searches.")
                    else:
                        artist_track_report(match["id"], match["name"])

            # Comparison artist report
            elif report_choice == "2":
                if len(searched_artists) >= 2:

                    # 1. Ask how to sort; default if blank or invalid
                    raw = input("Sort by followers or popularity? [default: followers]").strip().lower()
                    if raw in {"followers", "popularity"}:
                        sort_field = raw
                    else:
                        sort_field = "followers"
                    sort_col = "Followers" if sort_field == "followers" else "Popularity"

                    # 2. Ask order; default if blank or invalid
                    raw = input("Order asc or desc? [default: desc] ").strip().lower()
                    if raw not in {"asc", "desc"}:
                        order = raw
                    else:
                        order = "desc"
                    ascending = (order == "asc")

                    # 3. Build DataFrame
                    df = build_comparison_df(searched_artists)  # Followers/Popularity must be ints
                    df = sort_comparison_df(df, sort_col, ascending)
                    write_comparison_excel(df, "artist_comparison.xlsx")
                    print("Saved: artist_comparison.xlsx")

                    # 5) Write Excel
                    out_path = "artist_comparison.xlsx"
                    write_comparison_excel(df, out_path)
                    # print success message

                else:
                    print("You need at least two artists saved to generate a comparison report.")

        # 3. Print saved searches
        elif user_prompt == "saved":
            if not searched_artists:
                print("No artists saved yet.")
            else:
                for item in searched_artists:
                    print(item["name"])

        # 4. Delete artist
        elif user_prompt == "delete":
            for item in searched_artists:
                print(item["name"])

            print("")
            delete_choice = input("Which artist would you like to delete from your saved searches?: ").lower()

            for item in searched_artists:
                if item["name"].lower() == delete_choice:
                    searched_artists.remove(item)
                    print(f"{item['name']} has been deleted from your saved searches.")
                    break

        # 4. Quit
        elif user_prompt == "quit":
            print("Goodbye!")
            break

        else:
            print("Invalid response.")

if __name__ == "__main__":
    main()




