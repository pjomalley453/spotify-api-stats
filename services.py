from typing import Optional, Dict

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

