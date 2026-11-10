#!/usr/bin/env bash
# Creates the venv inside this folder and installs dependencies (macOS / Linux).
set -e
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python) || { echo "Python 3 not found."; exit 1; }
[ -d venv ] || "$PY" -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
echo
echo "Setup finished. Next:"
echo "  1. Open .env and add your OPENROUTER_API_KEY"
echo "  2. Run: source venv/bin/activate && python app.py"
