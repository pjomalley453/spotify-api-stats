import requests
import pandas as pd
from fpdf import FPDF

# PDF FUNCTIONS
def artist_track_pdf(artist_id, artist_name):
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


def generate_comparison_pdf(searched_artists):
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