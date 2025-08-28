import os
import pandas as pd
from dotenv import load_dotenv

from spotify_api import SpotifyAPI
import services

# Load secrets
load_dotenv()
client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

api = SpotifyAPI(client_id, client_secret)

artists = api.search_artists("four tet", limit=5)

if artists:
    artist_id = artists[0]["id"]  # take the first result’s ID
    df = services.build_top_tracks_df(api, artist_id)  # build top tracks DataFrame
    df = services.sort_top_tracks_df(df, sort_col="Popularity", ascending=False)

# Example: write excel (your writer function)
# services.write_top_tracks_excel(df, f"top_tracks_{artist_name}.xlsx")

query = "four tet"  # test query
url = "https://api.spotify.com/v1/search"
params = {"q": query, "type": "artist", "limit": 5}  # parsed list of dicts


# TOP TRACKS EXCEL FUNCTIONS


def write_top_tracks_excel(df, artist_name):
    """Write an artist's top tracks DataFrame to an Excel file with simple formatting."""
    if df.empty:
        print("No tracks found.")
        return

    # File name: replace spaces with underscores
    safe_name = artist_name.replace(" ", "_")
    path = f"top_tracks_{safe_name}.xlsx"

    with pd.ExcelWriter(path, engine="xlsxwriter") as xw:
        df.to_excel(xw, sheet_name="TopTracks", index=False)
        ws = xw.sheets["TopTracks"]

        # Formats
        header_fmt = xw.book.add_format({"bold": True})
        int_fmt = xw.book.add_format({"num_format": "0"})

        # Bold header row
        for col_idx, col_name in enumerate(df.columns):
            ws.write(0, col_idx, col_name, header_fmt)

        # Set reasonable column widths + formats
        ws.set_column(0, 0, 30)  # Track
        ws.set_column(1, 1, 30)  # Album
        ws.set_column(2, 2, 11, int_fmt)  # Popularity
        ws.set_column(3, 3, 14, int_fmt)  # Duration (min)

        # Freeze header row & add filter
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, len(df), len(df.columns) - 1)

    print(f"Saved: {path}")


# COMPARISON EXCEL FUNCTIONS
def build_comparison_df(searched_artists):
    """Returns pd.DataFrame with columns Artist, Followers, Popularity, Genres."""
    rows = []
    for a in searched_artists:
        artist_id = a["id"]

        # Call Spotify API for artist profile
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        data = api.get(url)

        # Extract fields
        name = data["name"]
        followers = int(data["followers"]["total"])
        popularity = int(data["popularity"])
        genres_list = data.get("genres", [])

        # Build rows
        rows.append({
            "Artist": name,
            "Followers": followers,
            "Popularity": popularity,
            "Genres": ", ".join(g.title() for g in genres_list) if genres_list else "N/A"
        })
    return pd.DataFrame(rows)


def sort_comparison_df(df, sort_col="Followers", ascending=False):
    """Sort the DataFrame by Followers or Popularity."""
    if sort_col not in {"Followers", "Popularity"}:
        sort_col = "Followers"

    df = df.sort_values(by=sort_col, ascending=ascending, ignore_index=True)
    return df


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


# MAIN LOOP
def main():
    searched_artists = []

    while True:
        print("")
        user_prompt = input("Choose an option: (search/report/saved/delete/quit) ").lower()

        # 1. Search for artist
        if user_prompt == "search":
            query = input("Enter an artist name: ").strip()
            artists = api.search_artists(query, limit=5)

            if not artists:
                print("No match found, try again. \n")
            else:
                artist = artists[0]

                # Print results
                print("")
                print("🎵 Artist:", artist["name"])
                print("👥 Followers:", f"{artist['followers']:,}")
                if artist["genres"]:
                    print("💿 Genres:", ", ".join(artist["genres"]))
                else:
                    print("💿 Genres: N/A")
                print("")
                print("🔗 URL:", artist["url"])
                print("")

                # Add to saved searches
                choice1 = input("Add this artist to your saved searches? (y/n): ").lower()
                if choice1 == "y":
                    if not any(a["id"] == artist["id"] for a in searched_artists):
                        searched_artists.append(artist)
                        print(f"{artist["name"]} added to saved searches.\n")
                    else:
                        print(f"{artist["name"]} is already in your saved searches.\n")

        # 2. Create report
        elif user_prompt == "report":
            print("")
            report_choice = input("Individual or comparison Excel report?: (1/2)")

            # Individual artist report
            if report_choice == "1":
                if not searched_artists:
                    print("No artists saved yet.")
                else:
                    for item in searched_artists:
                        print(item["name"])

                    name = input("Enter the artist name: ").strip().lower()
                    match = next((a for a in searched_artists if a["name"].lower() == name), None)

                    if not match:
                        print("Artist not in saved searches.")
                    else:

                        # 3. Build + sort
                        df = services.build_top_tracks_df(api, match["id"])

                        raw = input(
                            "Sort top tracks by (popularity/duration/none)? [default: popularity] ").strip().lower()
                        if raw == "duration":
                            df = services.build_top_tracks_df(api, match["id"])
                        elif raw in {"", "popularity"}:
                            df = services.sort_top_tracks_df(df, sort_col="Popularity", ascending=False)

                        # 4. Write Excel
                        write_top_tracks_excel(df, match["name"])

            # Comparison artist report
            elif report_choice == "2":
                if len(searched_artists) >= 2:

                    # 1. Ask how to sort; default if blank or invalid
                    print("")
                    raw = input("Sort by followers or popularity? [default: followers]").strip().lower()
                    if raw in {"followers", "popularity"}:
                        sort_field = raw
                    else:
                        sort_field = "followers"
                    sort_col = "Followers" if sort_field == "followers" else "Popularity"

                    # 2. Ask order; default if blank or invalid
                    print("")
                    raw = input("Order asc or desc? [default: desc] ").strip().lower()
                    order = raw if raw in {"asc", "desc"} else "desc"
                    ascending = (order == "asc")

                    # 3. Build + sort
                    df = build_comparison_df(searched_artists)  # Followers/Popularity must be ints
                    df = sort_comparison_df(df, sort_col, ascending)

                    # 4. Write Excel
                    write_comparison_excel(df, "artist_comparison.xlsx")
                    print("")
                    print("Saved: artist_comparison.xlsx")

                else:
                    print("You need at least two artists saved to generate a comparison report.")

        # 3. Print saved searches
        elif user_prompt == "saved":
            if not searched_artists:
                print("")
                print("No artists saved yet.")
            else:
                print("")
                print("Saved artists:")
                for item in searched_artists:
                    print(item["name"])

        # 4. Delete artist
        elif user_prompt == "delete":
            print("Saved artists:")
            for item in searched_artists:
                print(item["name"])

            print("")
            delete_choice = input("Enter the artist to delete: ").lower()

            for item in searched_artists:
                if item["name"].lower() == delete_choice:
                    searched_artists.remove(item)
                    print(f"{item['name']} has been deleted from your saved searches.")
                    break

        # 4. Quit
        elif user_prompt == "quit":
            print("")
            print("Goodbye!")
            break

        else:
            print("")
            print("Invalid response.")

if __name__ == "__main__":
    main()

