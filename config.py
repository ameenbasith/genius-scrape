# config.py - Configuration for Genius Lyrics Analyzer

import streamlit as st

# Try to get token from Streamlit secrets first, then fall back to hardcoded value
try:
    GENIUS_API_TOKEN = st.secrets["GENIUS_API_TOKEN"]
except:
    # Fallback for local development
    GENIUS_API_TOKEN = "sH5UlovGBUB1hfuxiEAnW80DyPnAUHr_-1OIFxqaca1lAhwtHzBmsNfGIzOsn-9U"  # Replace with your token for local testing

# Maximum number of songs to analyze by default
MAX_TOP_SONGS = 10

# Analysis weights
WEIGHTS = {
    'lexical_diversity': 0.7,
    'annotation_density': 0.3,
}