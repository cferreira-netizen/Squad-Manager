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