from typing import Optional, Dict
import pandas as pd
from main import client_id, client_secret
from spotify_api import SpotifyAPI

api = SpotifyAPI(client_id=client_id, client_secret=client_secret)

def parse_artists(data):
    if not isinstance(data, dict):
        raise TypeError("parse_artists expects a dict (raw Spotify JSON).")

    items = (data or {}).get("artists", {}).get("items", [])
    results = []
    for artist in items:
        results.append({
            "id": artist["id"],
            "name": artist["name"],
            "url": artist["external_urls"]["spotify"],
            "genres": artist.get("genres", []),
            "followers": int(artist.get("followers", {}).get("total", 0)),
            "popularity": int(artist.get("popularity", 0))
        })
    return results


def find_best_artist(api, query: str, limit: int = 5) -> Optional[Dict]:
    """
    Uses SpotifyAPI.search_artists_raw, then picks one artist and
    returns a tidy dict: {id, name, followers, popularity, genres, url}.
    Returns None if no results.
    """
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