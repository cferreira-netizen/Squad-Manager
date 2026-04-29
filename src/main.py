import os
import json
import pandas as pd
import streamlit as st
from datetime import date

# path helpers

APP_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_path(filename: str) -> str:
    """returns the absolute path to a file inside the data/ """

    return os.path.join(APP_PATH, "data", filename)

# DATA Persistence

SQUAD_FILE = get_data_path("squad.json")
MATCHES_FILE = get_data_path("matches.json")

def load_json(filename: str, default):
    """Load JSON from disk returning default if file dosen't exist."""
    
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename: str, data):
    """Save JSON to disk."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=str)

# Session State

def init_state():
    """Initialize session state variables."""
    if "squad" not in st.session_state:
        st.session_state.squad = load_json(SQUAD_FILE, [])
    if "matches" not in st.session_state:
        st.session_state.matches = load_json(MATCHES_FILE, [])

# Helper utilities 

POSITIONS = ["GK", "CB","LB", "RB", "CDM","CM", "CAM", "LW", "RW", "ST"]

FITNESS_LEVELS = ["🟢 Fit", "🟡 Slight knock", "🔴 Injured", "⚪ Unknown"]

def get_squad_df():
    """Convert squad list to a DataFrame."""
    if st.session_state.squad:
        return pd.DataFrame(st.session_state.squad)
    return pd.DataFrame(columns=["name", "position", "fitness", "availability", "notes", "form"])

def calculate_form(player_name: str):
    """Calculate player form based on recent matches."""
    score = 5.0 # Base score
    revelant = [m for m in st.session_state.matches if player_name in m.get("squad",[])][-5:]
    if not revelant:
        return score
    total = 0.0
    for match in revelant:
        pts = 0
        for match in revelant:
            pts = 0
            if match.get("result") == "W":
                pts += 3
            elif match.get("result") == "D":
                pts += 1
            goals = match.get("scorers",{}).get(player_name, 0)
            assists = match.get("assisters",{}).get(player_name, 0)
