import os
import json
import pandas as pd
import streamlit as st
from datetime import date

# path helpers

APP_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_path():
    """returns the absolute path to a file inside the data/ """

    return os.path.join(APP_PATH, "data", filename)
