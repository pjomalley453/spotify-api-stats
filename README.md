# Spotify Artist Stats Tool

A Python CLI app that uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api) to fetch artist data and generate reports.  
Features **API integration**, **Pandas data wrangling**, and **automated Excel reporting**.

---

## Quickstart

```bash
# 1) Clone
git clone https://github.com/pjomalley453/spotify-api-stats.git
cd spotify-api-stats

# 2) Env vars
cp .env.example .env
# then edit .env with your Spotify credentials:
# SPOTIFY_CLIENT_ID=...
# SPOTIFY_CLIENT_SECRET=...

# 3) Setup (venv + deps)
./setup.sh
source .venv/bin/activate

# 4) Run
python main.py
