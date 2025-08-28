from typing import Optional, Dict
import pandas as pd
import re


def find_best_artist(api, query: str, limit: int = 5) -> Optional[Dict]:
    """
    Uses SpotifyAPI.search_artists_raw, then picks one artist and
    returns a tidy dict: {id, name, followers, popularity, genres, url}.
    Returns None if no results.
    """
    q = (query or "").strip()
    if not q:
        return None

    data = api.search_artists_raw(query, limit=limit)
    items = (data or {}).get("artists", {}).get("items", [])
    if not items:
        return None

    # Strategy: prefer exact (case-insensitive) name match; otherwise highest popularity.
    exact = next((a for a in items if a.get("name", "").lower() == query.strip().lower()), None)
    artist = exact or max(items, key=lambda a: a.get("popularity", 0))

    return {
        "id": artist["id"],
        "name": artist["name"],
        "followers": artist.get("followers", {}).get("total", 0),
        "popularity": artist.get("popularity", 0),
        "genres": artist.get("genres", []),
        "url": artist.get("external_urls", {}).get("spotify", "")
    }


# Top Tracks (Per Artist)
def build_top_tracks_df(api, artist_id: str, market: str = "US"):
    if not artist_id:
        if not artist_id:
            raise ValueError("artist_id is required")

    data = api.get_artist_top_tracks(artist_id, market=market)
    tracks = (data or {}).get("tracks", []) or []

    rows = []
    for t in tracks:
        rows.append({
            "Track": t.get("name", ""),
            "Album": (t.get("album") or {}).get("name", ""),
            "Popularity": int(t.get("popularity", 0)),
            "Duration (min)": int(t.get("duration_ms") or 0 // 60000),
        })

    return pd.DataFrame(rows)

def sort_top_tracks_df(df: pd.DataFrame, sort_col: str = "Popularity", ascending: bool = False) -> pd.DataFrame:
    """Sort the top-tracks DataFrame by a supported column."""
    allowed = {"Track", "Album", "Popularity", "Duration (min)"}
    if sort_col not in allowed:
        sort_col = "Popularity"
    return df.sort_values(by=sort_col, ascending=ascending, ignore_index=True)

def write_top_tracks_excel(df: pd.DataFrame, artist_name):
    """Write an artist's top tracks DataFrame to an Excel file with simple formatting."""
    if df.empty:
        print("No tracks found.")
        return

    # File name: replace spaces with underscores
    safe_name = re.sub(r'[^A-Za-z0-9._-]+', "_", artist_name).strip("_")
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
    return path


# Artist Comparison
def build_comparison_df(api, searched_artists):
    """Returns pd.DataFrame with columns Artist, Followers, Popularity, Genres."""
    rows = []
    for a in searched_artists:
        artist_id = a["id"]

        # Call Spotify API for artist profile
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        data = api.get(url) or {}

        # Extract fields
        name = data.get("name", "Unknown")
        followers = int(data.get("followers", {}).get("total", 0))
        popularity = int(data.get("popularity", 0))
        genres_list = data.get("genres", []) or []

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

def write_comparison_excel(df: pd.DataFrame, path: str = "artist_comparison.xlsx") -> str:
    """
    Write the multi-artist comparison DataFrame to an Excel file with light formatting.
    Expects columns: Artist, Followers, Popularity, Genres.
    Returns the path written.
    """
    if df is None or df.empty:
        print("No data to write.")
        return path

    with pd.ExcelWriter(path, engine="xlsxwriter") as xw:
        df.to_excel(xw, sheet_name="Comparison", index=False)
        ws = xw.sheets["Comparison"]

        # Formats
        header_fmt = xw.book.add_format({"bold": True})
        num_fmt = xw.book.add_format({"num_format": "#,##0"})  # comma thousands

        # Bold header row
        for col_idx, col_name in enumerate(df.columns):
            ws.write(0, col_idx, col_name, header_fmt)

        # Column widths + number format for Followers (if present)
        cols = list(df.columns)
        if "Artist" in cols:
            ws.set_column(cols.index("Artist"), cols.index("Artist"), 22)
        if "Followers" in cols:
            idx = cols.index("Followers")
            ws.set_column(idx, idx, 14, num_fmt)
        if "Popularity" in cols:
            idx = cols.index("Popularity")
            ws.set_column(idx, idx, 11)
        if "Genres" in cols:
            idx = cols.index("Genres")
            ws.set_column(idx, idx, 40)

        # Freeze header row & add filter
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, len(df), len(df.columns) - 1)

    print(f"Saved: {path}")
    return path

