# genius_analyzer.py - Core functionality for analyzing lyrics from Genius

import pandas as pd
from lyricsgenius import Genius
import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import string
from nltk.corpus import stopwords
from config import WEIGHTS

# Download required NLTK data on first run
try:
    nltk.data.find('vader_lexicon')
    nltk.data.find('stopwords')
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download('vader_lexicon')
    nltk.download('stopwords')


class GeniusLyricsAnalyzer:
    def __init__(self, token):
        """Initialize with your Genius API token"""
        self.genius = Genius(token)
        self.genius.verbose = False  # Turn off status messages
        self.genius.remove_section_headers = True  # Remove [Chorus], [Verse], etc.

    def get_song(self, artist_name, song_name):
        """Get a specific song by artist and title"""
        return self.genius.search_song(song_name, artist_name)

    def get_album(self, artist_name, album_name):
        """Get all songs from an album"""
        return self.genius.search_album(album_name, artist_name)

    # Add this to your get_artist_songs method
    def get_artist_songs(self, artist_name, max_songs=10):
        """Get songs by an artist (limited to max_songs)"""
        try:
            artist = self.genius.search_artist(artist_name, max_songs=max_songs)
            return artist.songs if artist else []
        except Exception as e:
            print(f"Error accessing Genius API: {str(e)}")
            # Add more detailed error handling if needed
            return []

    def process_song(self, song, status_callback=None):
        """Process a song to extract lyrics and annotations"""
        if not song:
            if status_callback:
                status_callback("Song not found")
            return None

        if status_callback:
            status_callback(f"Processing song: {song.title}")

        # Get song metadata
        song_data = {
            'song_id': getattr(song, 'id', ''),
            'title': getattr(song, 'title', 'Unknown Title'),
            'artist': getattr(song, 'artist', 'Unknown Artist'),
            'album': getattr(song, 'album', ''),
            'release_date': getattr(song, 'release_date', ''),
            'lyrics': getattr(song, 'lyrics', '')
        }

        # Get annotations
        if status_callback:
            status_callback(f"Getting annotations for: {song.title}")

        annotations = self.genius.song_annotations(song.id)

        # Create a mapping of lyric fragments to annotations
        annotation_map = {}
        for lyric, explanations in annotations:
            if explanations:  # Only include if there are explanations
                # Join multiple explanations if there are any
                combined_explanation = " ".join([exp[0] for exp in explanations if exp])
                annotation_map[lyric] = combined_explanation

        song_data['annotation_map'] = annotation_map

        return song_data

    def analyze_song_complexity(self, song_data, status_callback=None):
        """Analyze the complexity of a song based on various metrics"""
        if not song_data or 'lyrics' not in song_data:
            return {}

        if status_callback:
            status_callback(f"Analyzing complexity of: {song_data.get('title', 'Unknown')}")

        lyrics = song_data['lyrics']

        # Clean lyrics
        lyrics_clean = re.sub(r'\[.*?\]', '', lyrics)  # Remove section headers
        lyrics_clean = re.sub(r'[^\w\s]', '', lyrics_clean)  # Remove punctuation
        lyrics_clean = lyrics_clean.lower()

        # Calculate metrics
        word_count = len(lyrics_clean.split())
        unique_words = len(set(lyrics_clean.split()))

        # Calculate lexical diversity (unique words / total words)
        lexical_diversity = unique_words / word_count if word_count > 0 else 0

        # Calculate average word length
        avg_word_length = sum(len(word) for word in lyrics_clean.split()) / word_count if word_count > 0 else 0

        # Calculate annotation richness (percentage of lyrics with annotations)
        annotation_map = song_data.get('annotation_map', {})
        annotation_coverage = len(annotation_map) / word_count if word_count > 0 else 0

        # Sentiment analysis
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(lyrics_clean)

        complexity_scores = {
            'word_count': word_count,
            'unique_words': unique_words,
            'lexical_diversity': lexical_diversity,
            'avg_word_length': avg_word_length,
            'annotation_coverage': annotation_coverage,
            'sentiment': sentiment
        }

        return complexity_scores

    def get_top_words(self, song_data, n=10, status_callback=None):
        """Get the top N most frequent words in a song"""
        if not song_data or 'lyrics' not in song_data:
            return []

        if status_callback:
            status_callback(f"Finding top words in: {song_data.get('title', 'Unknown')}")

        # Clean lyrics
        lyrics = song_data['lyrics']
        lyrics_clean = re.sub(r'\[.*?\]', '', lyrics)  # Remove section headers
        lyrics_clean = re.sub(r'[^\w\s]', '', lyrics_clean)  # Remove punctuation
        lyrics_clean = lyrics_clean.lower()

        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        words = [word for word in lyrics_clean.split() if word not in stop_words and len(word) > 1]

        # Count word frequencies
        word_counts = Counter(words)

        # Return top N words
        return word_counts.most_common(n)

    def create_song_dataframe(self, song_data_list, status_callback=None):
        """Create a DataFrame from processed songs with analysis"""
        if not song_data_list:
            return pd.DataFrame()

        if status_callback:
            status_callback("Creating song analysis dataframe")

        rows = []
        for song_data in song_data_list:
            if not song_data:
                continue

            # Extract basic info
            row = {
                'song_id': song_data.get('song_id', ''),
                'title': song_data.get('title', ''),
                'artist': song_data.get('artist', ''),
                'album': song_data.get('album', ''),
                'release_date': song_data.get('release_date', ''),
                'word_count': 0,
                'unique_word_count': 0,
                'lexical_diversity': 0,
                'annotation_count': 0,
                'sentiment_compound': 0
            }

            # Add complexity metrics if available
            complexity = song_data.get('complexity', {})
            if complexity:
                row['word_count'] = complexity.get('word_count', 0)
                row['unique_word_count'] = complexity.get('unique_words', 0)
                row['lexical_diversity'] = complexity.get('lexical_diversity', 0)
                row['annotation_count'] = len(song_data.get('annotation_map', {}))
                sentiment = complexity.get('sentiment', {})
                row['sentiment_compound'] = sentiment.get('compound', 0) if sentiment else 0

            rows.append(row)

        return pd.DataFrame(rows)

    def create_annotations_dataframe(self, song_data_list, status_callback=None):
        """Create a DataFrame with lyrics and their annotations"""
        if not song_data_list:
            return pd.DataFrame()

        if status_callback:
            status_callback("Creating annotations dataframe")

        rows = []
        for song_data in song_data_list:
            if not song_data:
                continue

            annotation_map = song_data.get('annotation_map', {})
            for lyric, explanation in annotation_map.items():
                rows.append({
                    'song_id': song_data.get('song_id', ''),
                    'title': song_data.get('title', ''),
                    'artist': song_data.get('artist', ''),
                    'lyric_fragment': lyric,
                    'annotation': explanation
                })

        return pd.DataFrame(rows)

    def rank_songs_by_complexity(self, songs_df, status_callback=None):
        """Rank songs by complexity metrics and return a composite score"""
        if songs_df.empty:
            return pd.DataFrame()

        if status_callback:
            status_callback("Ranking songs by complexity")

        # Create normalized scores (0-1) for each metric
        songs_df['norm_lexical_diversity'] = (songs_df['lexical_diversity'] - songs_df['lexical_diversity'].min()) / \
                                             (songs_df['lexical_diversity'].max() - songs_df['lexical_diversity'].min()) \
            if songs_df['lexical_diversity'].max() != songs_df['lexical_diversity'].min() else 0

        songs_df['norm_annotation_density'] = (songs_df['annotation_count'] / songs_df['word_count']) \
            if songs_df['word_count'].max() > 0 else 0

        # Create a composite score using weights from config
        songs_df['complexity_score'] = (
                songs_df['norm_lexical_diversity'] * WEIGHTS['lexical_diversity'] +
                songs_df['norm_annotation_density'] * WEIGHTS['annotation_density']
        )

        # Rank songs by complexity score
        ranked_songs = songs_df.sort_values('complexity_score', ascending=False).reset_index(drop=True)

        return ranked_songs

    def visualize_song_complexity(self, ranked_songs, top_n=10, save_path='song_complexity_analysis.png',
                                  status_callback=None):
        """Create visualizations of song complexity metrics"""
        if ranked_songs.empty or len(ranked_songs) < 2:
            if status_callback:
                status_callback("Not enough songs to visualize")
            return False

        if status_callback:
            status_callback("Creating visualizations")

        # Limit to top N songs
        top_songs = ranked_songs.head(min(top_n, len(ranked_songs)))

        # Create figure with subplots
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: Complexity Score
        top_songs.plot(x='title', y='complexity_score', kind='bar', ax=axes[0],
                       title='Song Complexity Scores', color='skyblue')
        axes[0].set_xlabel('Song')
        axes[0].set_ylabel('Complexity Score')
        axes[0].set_xticklabels(top_songs['title'], rotation=45, ha='right')

        # Plot 2: Lexical Diversity vs Annotation Density
        scatter = axes[1].scatter(top_songs['norm_lexical_diversity'],
                                  top_songs['norm_annotation_density'],
                                  s=100, alpha=0.7)

        # Add labels for each point
        for i, row in top_songs.iterrows():
            axes[1].annotate(row['title'],
                             (row['norm_lexical_diversity'], row['norm_annotation_density']),
                             xytext=(5, 5), textcoords='offset points')

        axes[1].set_xlabel('Lexical Diversity (normalized)')
        axes[1].set_ylabel('Annotation Density (normalized)')
        axes[1].set_title('Lexical Diversity vs Annotation Density')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

        if status_callback:
            status_callback(f"Visualization saved as '{save_path}'")

        return True

    def run_analysis(self, artist_name, album_name=None, song_name=None, max_songs=10, status_callback=None,
                     save_files=False):
        """Run a complete analysis on an artist, album, or song"""
        processed_songs = []

        if album_name:
            if status_callback:
                status_callback(f"Analyzing album '{album_name}' by {artist_name}...")

            album = self.get_album(artist_name, album_name)
            if album and hasattr(album, 'tracks'):
                for song in album.tracks:
                    if status_callback:
                        status_callback(f"Processing song: {song.title}")

                    song_data = self.process_song(song, status_callback)
                    if song_data:
                        song_data['complexity'] = self.analyze_song_complexity(song_data, status_callback)
                        processed_songs.append(song_data)
            else:
                if status_callback:
                    status_callback(f"Album '{album_name}' not found or has no tracks")

        elif song_name:
            if status_callback:
                status_callback(f"Analyzing song '{song_name}' by {artist_name}...")

            song = self.get_song(artist_name, song_name)
            if song:
                song_data = self.process_song(song, status_callback)
                if song_data:
                    song_data['complexity'] = self.analyze_song_complexity(song_data, status_callback)
                    processed_songs.append(song_data)
            else:
                if status_callback:
                    status_callback(f"Song '{song_name}' not found")

        else:
            if status_callback:
                status_callback(f"Analyzing top {max_songs} songs by {artist_name}...")

            songs = self.get_artist_songs(artist_name, max_songs=max_songs)
            if songs:
                for song in songs:
                    if status_callback:
                        status_callback(f"Processing song: {song.title}")

                    song_data = self.process_song(song, status_callback)
                    if song_data:
                        song_data['complexity'] = self.analyze_song_complexity(song_data, status_callback)
                        processed_songs.append(song_data)
            else:
                if status_callback:
                    status_callback(f"No songs found for artist: {artist_name}")

        # Create DataFrames
        songs_df = self.create_song_dataframe(processed_songs, status_callback)
        annotations_df = self.create_annotations_dataframe(processed_songs, status_callback)

        # Prepare output files dictionary but don't save files by default
        output_files = {}

        # Only save files if explicitly requested
        if save_files and not songs_df.empty:
            songs_file = f"{artist_name.replace(' ', '_')}_songs_analysis.csv"
            songs_df.to_csv(songs_file, index=False)
            output_files['songs_file'] = songs_file
            if status_callback:
                status_callback(f"Saved song analysis to {songs_file}")

            if not annotations_df.empty:
                annotations_file = f"{artist_name.replace(' ', '_')}_annotations.csv"
                annotations_df.to_csv(annotations_file, index=False)
                output_files['annotations_file'] = annotations_file
                if status_callback:
                    status_callback(f"Saved annotations to {annotations_file}")

        # Rank songs by complexity
        ranked_songs = None
        if len(processed_songs) > 1:
            ranked_songs = self.rank_songs_by_complexity(songs_df, status_callback)
            if status_callback and not ranked_songs.empty:
                status_callback("\nSongs Ranked by Complexity Score:")
                for i, row in ranked_songs.iterrows():
                    status_callback(f"{i + 1}. {row['title']} - Complexity Score: {row['complexity_score']:.4f}")

            # Create visualization but only save file if requested
            visualization_file = f"{artist_name.replace(' ', '_')}_complexity_analysis.png"
            vis_success = self.visualize_song_complexity(ranked_songs, save_path=visualization_file,
                                                         status_callback=status_callback)
            if vis_success and save_files:
                output_files['visualization_file'] = visualization_file
            elif vis_success:
                # Still store the path even if not saved, so the UI knows the file exists temporarily
                output_files['visualization_file'] = visualization_file

        return {
            'processed_songs': processed_songs,
            'songs_df': songs_df,
            'annotations_df': annotations_df,
            'ranked_songs': ranked_songs,
            'output_files': output_files
        }