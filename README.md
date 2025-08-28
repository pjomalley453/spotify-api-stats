# Spotify Artist Stats Tool

A Python CLI app that uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api) to fetch artist data and generate Excel reports.  
Demonstrates **API integration**, **Pandas data wrangling**, and **automated Excel reporting**.

---

## Quickstart

```bash
# 1) Clone repo
git clone https://github.com/pjomalley453/spotify-api-stats.git
cd spotify-api-stats

# 2) Environment variables
cp .env.example .env
# then edit .env with your Spotify credentials:
# SPOTIFY_CLIENT_ID=your_client_id
# SPOTIFY_CLIENT_SECRET=your_client_secret

# Note: You’ll need to generate your own Spotify API credentials at https://developer.spotify.com/dashboard/.
# Copy them into .env using the .env.example template.

# 3) Create venv + install dependencies
./setup.sh

# 4) Activate venv
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\activate

# 5) Install
pip install -e .

# 6) Run
python main.py
