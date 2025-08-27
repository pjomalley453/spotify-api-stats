# Spotify Artist Stats Tool

A Python program that uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api) to fetch artist data and generate PDF reports.  
Highlights **API integration**, **data analysis with Pandas**, and **automated reporting with FPDF2**.

---

## Features
- 🔎 Search artists by name  
- 📊 View details: followers, popularity, genres, profile link  
- 📝 Generate PDF reports:
  - Top Tracks (track, album, popularity, duration)  
  - Multi-Artist Comparison (followers, popularity, genres)  
- ✅ Prevents duplicates & handles invalid searches

---

## Tech Stack
- Python 3.11+  
- Requests • Pandas • FPDF2 • python-dotenv  

---

## Setup

### Clone & Install
```bash
git clone https://github.com/<you>/spotify-api-stats.git
cd spotify-api-stats
cp .env.example .env
./setup.sh
source .venv/bin/activate
```
With Pip:
```bash
pip install -r requirements.txt
```
With conda:
```bash
conda env create -f environment.yml
conda activate spotify-api-stats
```
Create a .env in the project root:
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

Usage:
```bash
python main.py
