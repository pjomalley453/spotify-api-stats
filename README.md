# Spotify Artist Stats Tool

A Python program that integrates with the [Spotify Web API](https://developer.spotify.com/documentation/web-api) to fetch artist data and generate PDF reports.  
Demonstrates **API integration**, **data processing (Pandas)**, and **automation/reporting (FPDF2)**.

---

## Features
- Search artists by name via Spotify API
- View artist details: followers, popularity, genres, profile link
- Generate reports:
  - **Top Tracks PDF** — track, album, popularity, duration  
  - **Comparison PDF** — compare multiple saved artists, sorted by Followers or Popularity
- Prevents duplicates and handles invalid searches

---

## Tech Stack
- Python 3.13  
- Requests • Pandas • FPDF2 • python-dotenv  

---

## Setup
1. Clone repo & install:
   ```bash
   git clone git@github.com:yourusername/spotify-api-stats.git
   cd spotify-api-stats
   pip install -r requirements.txt
