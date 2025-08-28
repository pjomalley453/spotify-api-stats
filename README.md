# Spotify Artist Stats Tool

A Python CLI app that uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api) to fetch artist data and generate Excel reports.  
Features **API integration**, **Pandas data wrangling**, and **automated Excel reporting**.

---

## Quickstart

```bash
# 1) Clone
git clone https://github.com/pjomalley453/spotify-api-stats.git
cd spotify-api-stats

# 2) Environment variables
cp .env.example .env
# then edit .env with your Spotify credentials:
# SPOTIFY_CLIENT_ID=your_client_id_here
# SPOTIFY_CLIENT_SECRET=your_client_secret_here

# 3) Create venv + install dependencies
./setup.sh
source .venv/bin/activate

# 4) Install in editable mode (makes spotify_tool importable anywhere)
pip install -e .

# 5) Run
python main.py