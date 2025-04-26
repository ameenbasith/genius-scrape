# config.py - Configuration for Genius Lyrics Analyzer

# Genius API token
GENIUS_API_TOKEN = "sH5UlovGBUB1hfuxiEAnW80DyPnAUHr_-1OIFxqaca1lAhwtHzBmsNfGIzOsn-9U"

# Maximum number of songs to analyze by default
MAX_TOP_SONGS = 10

# Analysis weights - adjust these to change how the complexity score is calculated
WEIGHTS = {
    'lexical_diversity': 0.7,  # How diverse the vocabulary is
    'annotation_density': 0.3,  # How many annotations the song has relative to length
}