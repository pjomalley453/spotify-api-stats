import requests, time

class SpotifyArtistTool:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.expires_at = 0

    def _get_spotify_token(self):
        if self.access_token and time.time() < self.expires_at:
            return self.access_token

        token_url = "https://accounts.spotify.com/api/token"
        data = {"grant_type": "client_credentials"}
        resp = requests.post(token_url, data=data, auth=(self.client_id, self.client_secret))

        if resp.status_code != 200:
            raise Exception(f"Failed to get token: {resp.status_code}, {resp.text}")

        token_json = resp.json()
        self.access_token = token_json["access_token"]
        expires_in = token_json["expires_in"]
        self.expires_at = time.time() + expires_in - 30

        return self.access_token

    def _headers(self):
        # Always ensure a fresh token
        token = self._get_spotify_token()
        return {"Authorization": f"Bearer {token}"}

    def get(self, url, params=None):
        import requests
        resp = requests.get(url, headers=self._headers(), params=params, timeout=20)

        # Optional: auto-retry once on 401 (token just expired on server side)
        if resp.status_code == 401:
            # force refresh and retry
            self.access_token = None
            resp = requests.get(url, headers=self._headers(), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def search_artists_raw(self, query: str, limit: int = 5):
        query = (query or "").strip()
        if not query:
            return {}
        url = "https://api.spotify.com/v1/search"
        params = {"q": query, "type": "artist", "limit": limit}
        return self.get(url, params=params)

