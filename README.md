# Spotify Artist Stats Tool

A small Python app that uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api) to fetch artist data and generate reports.  
Highlights **API integration**, **Pandas data wrangling**, and **automated PDF reporting (FPDF2)**.

---

## Quickstart

```bash
# 1) Clone
git clone https://github.com/<you>/spotify-api-stats.git
cd spotify-api-stats

# 2) Env vars
cp .env.example .env
# then edit .env with your Spotify credentials:
# SPOTIFY_CLIENT_ID=...
# SPOTIFY_CLIENT_SECRET=...

# 3) One-shot setup (venv + deps)
./setup.sh
source .venv/bin/activate

# 4) Run
python main.py
