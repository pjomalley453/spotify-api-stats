#!/usr/bin/env bash
set -euo pipefail

# 1) Create venv if missing
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# 2) Activate
# shellcheck disable=SC1091
source .venv/bin/activate

# 3) Upgrade pip + install deps
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4) Gentle reminder about env
if [ ! -f ".env" ]; then
  echo "No .env found. Copied .env.example -> .env. Please edit it with your Spotify keys."
  cp .env.example .env
fi

echo "   Setup complete. Next:"
echo "   source .venv/bin/activate"
echo "   python main.py"
