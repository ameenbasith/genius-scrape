# app.py - Streamlit web application for Genius Lyrics Analyzer
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
from genius_analyzer import GeniusLyricsAnalyzer
from config import GENIUS_API_TOKEN, MAX_TOP_SONGS, WEIGHTS

# Page configuration
st.set_page_config(
    page_title="Genius Lyrics Analyzer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1DB954;
    }
    .status-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        max-height: 200px;
        overflow-y: auto;
    }
    .annotation-box {
        background-color: #f9f9f9;
        border-left: 3px solid #1DB954;
        padding: 10px;
        margin: 5px 0;
    }
    .lyric-fragment {
        font-weight: bold;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
def update_status(message):
    """Update the status display with a new message"""
    if 'status_messages' not in st.session_state:
        st.session_state.status_messages = []
    st.session_state.status_messages.append(message)

    # Update the status area if it exists
    if 'status_area' in st.session_state:
        status_html = ""
        for msg in st.session_state.status_messages[-10:]:  # Show last 10 messages
            status_html += f"<p>{msg}</p>"
        st.session_state.status_area.markdown(f'<div class="status-box">{status_html}</div>', unsafe_allow_html=True)


# Sidebar for configuration
st.sidebar.title("Genius Lyrics Analyzer")

# API token input
token = st.sidebar.text_input("Genius API Token", value=GENIUS_API_TOKEN, type="password")

# Analysis type selection
analysis_type = st.sidebar.radio(
    "Analysis Type",
    options=["Artist's Top Songs", "Album", "Single Song"],
    index=0
)

# Input fields
artist_name = st.sidebar.text_input("Artist Name")

if analysis_type == "Album":
    album_name = st.sidebar.text_input("Album Name")
    song_name = None
    max_songs = MAX_TOP_SONGS
elif analysis_type == "Single Song":
    album_name = None
    song_name = st.sidebar.text_input("Song Name")
    max_songs = MAX_TOP_SONGS
else:  # Artist's Top Songs
    album_name = None
    song_name = None
    max_songs = st.sidebar.slider("Number of Songs to Analyze", min_value=1, max_value=50, value=MAX_TOP_SONGS)

# Advanced options in an expandable section
with st.sidebar.expander("Advanced Options"):
    lexical_weight = st.slider(
        "Lexical Diversity Weight",
        min_value=0.0,
        max_value=1.0,
        value=WEIGHTS['lexical_diversity'],
        step=0.1,
        help="How much importance to give to vocabulary richness"
    )

    annotation_weight = st.slider(
        "Annotation Density Weight",
        min_value=0.0,
        max_value=1.0,
        value=WEIGHTS['annotation_density'],
        step=0.1,
        help="How much importance to give to annotation coverage"
    )

    # Normalize weights to sum to 1
    total = lexical_weight + annotation_weight
    if total > 0:
        WEIGHTS['lexical_diversity'] = lexical_weight / total
        WEIGHTS['annotation_density'] = annotation_weight / total

# Run button
run_analysis = st.sidebar.button("Run Analysis", type="primary")

# Add an option to save files
save_files = st.sidebar.checkbox("Save files to disk", value=False,
                                 help="If checked, CSV and image files will be saved to disk. Otherwise, they'll only be available for download.")

# Main content area
st.title("Genius Lyrics Analyzer")
st.markdown("Analyze the complexity and annotations of song lyrics from Genius.com")

# Initialize session state for status messages
if 'status_messages' not in st.session_state:
    st.session_state.status_messages = []

if 'results' not in st.session_state:
    st.session_state.results = None

# Status area
status_container = st.container()
with status_container:
    st.session_state.status_area = st.empty()

# Results tabs
results_tabs = st.tabs(["Overview", "Song Rankings", "Visualizations", "Annotations", "Songwriter's Workshop"])

# Run the analysis when the button is clicked
if run_analysis:
    # Reset status messages
    st.session_state.status_messages = []

    # Validate inputs
    if not token:
        st.error("Please enter your Genius API token")
    elif not artist_name:
        st.error("Please enter an artist name")
    elif analysis_type == "Album" and not album_name:
        st.error("Please enter an album name")
    elif analysis_type == "Single Song" and not song_name:
        st.error("Please enter a song name")
    else:
        # Show progress
        progress_bar = st.progress(0)

        # Initialize analyzer
        update_status("Initializing analyzer...")
        analyzer = GeniusLyricsAnalyzer(token)


        # Create a status callback that also updates progress
        def status_callback(message):
            update_status(message)
            # Simple heuristic to update progress
            if "Initializing" in message:
                progress_bar.progress(10)
            elif "Searching" in message or "found artist" in message:
                progress_bar.progress(20)
            elif "Processing song" in message:
                progress_bar.progress(30)
            elif "Getting annotations" in message:
                progress_bar.progress(50)
            elif "Analyzing complexity" in message:
                progress_bar.progress(70)
            elif "Creating" in message and "dataframe" in message:
                progress_bar.progress(80)
            elif "Ranking songs" in message:
                progress_bar.progress(90)
            elif "Visualization saved" in message:
                progress_bar.progress(100)


        # Run the appropriate analysis with save_files parameter
        try:
            update_status(f"Starting analysis for {artist_name}...")

            if analysis_type == "Artist's Top Songs":
                results = analyzer.run_analysis(
                    artist_name,
                    max_songs=max_songs,
                    status_callback=status_callback,
                    save_files=save_files
                )
            elif analysis_type == "Album":
                results = analyzer.run_analysis(
                    artist_name,
                    album_name=album_name,
                    status_callback=status_callback,
                    save_files=save_files
                )
            elif analysis_type == "Single Song":
                results = analyzer.run_analysis(
                    artist_name,
                    song_name=song_name,
                    status_callback=status_callback,
                    save_files=save_files
                )

            # Store results in session state
            st.session_state.results = results

            # Complete progress
            progress_bar.progress(100)
            update_status("Analysis complete!")

            # Force a rerun to update all tabs with the new results
            time.sleep(1)
            st.rerun()  # Using st.rerun() instead of st.experimental_rerun()

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            update_status(f"Error: {str(e)}")
            progress_bar.empty()

# Display results if available
if st.session_state.results:
    results = st.session_state.results
    songs_df = results.get('songs_df')
    ranked_songs = results.get('ranked_songs')
    annotations_df = results.get('annotations_df')
    output_files = results.get('output_files', {})

    # Check if we have valid results
    if songs_df is not None and not songs_df.empty:
        # Overview tab
        with results_tabs[0]:
            st.header("Analysis Overview")

            # Basic stats
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Songs Analyzed", f"{len(songs_df)}")
                st.metric("Average Word Count", f"{songs_df['word_count'].mean():.1f}")
                st.metric("Average Unique Words", f"{songs_df['unique_word_count'].mean():.1f}")

            with col2:
                st.metric("Average Lexical Diversity", f"{songs_df['lexical_diversity'].mean():.4f}")
                st.metric("Average Annotations", f"{songs_df['annotation_count'].mean():.1f}")

                # Calculate sentiment
                if 'sentiment_compound' in songs_df.columns:
                    avg_sentiment = songs_df['sentiment_compound'].mean()
                    sentiment_label = "Positive" if avg_sentiment > 0.05 else "Negative" if avg_sentiment < -0.05 else "Neutral"
                    st.metric("Average Sentiment", sentiment_label)

            # Top songs
            if ranked_songs is not None and not ranked_songs.empty:
                st.subheader("Top Songs by Complexity")

                # Show top 5 songs
                top_songs = ranked_songs.head(5)
                for i, row in top_songs.iterrows():
                    st.markdown(f"**{i + 1}. {row['title']}** - Complexity Score: {row['complexity_score']:.4f}")

                    # Show a tooltip with more info on hover
                    st.markdown(f"""
                    <div style="margin-left: 20px; margin-bottom: 10px; font-size: 0.9em; color: gray;">
                        Word Count: {int(row['word_count'])} | 
                        Unique Words: {int(row['unique_word_count'])} | 
                        Lexical Diversity: {row['lexical_diversity']:.4f} | 
                        Annotations: {int(row['annotation_count'])}
                    </div>
                    """, unsafe_allow_html=True)

            # Output files
            if output_files:
                st.subheader("Output Files")
                for file_type, file_path in output_files.items():
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as file:
                            if file_path.endswith(".csv"):
                                btn = st.download_button(
                                    label=f"Download {os.path.basename(file_path)}",
                                    data=file,
                                    file_name=os.path.basename(file_path),
                                    mime="text/csv"
                                )
                            elif file_path.endswith(".png"):
                                btn = st.download_button(
                                    label=f"Download {os.path.basename(file_path)}",
                                    data=file,
                                    file_name=os.path.basename(file_path),
                                    mime="image/png"
                                )

        # Song Rankings tab
        with results_tabs[1]:
            st.header("Song Rankings")

            if ranked_songs is not None and not ranked_songs.empty:
                # Display the table
                display_df = ranked_songs.copy()

                # Format columns
                display_df['Rank'] = range(1, len(display_df) + 1)
                display_df['lexical_diversity'] = display_df['lexical_diversity'].map('{:.4f}'.format)
                display_df['complexity_score'] = display_df['complexity_score'].map('{:.4f}'.format)

                # Select and rename columns
                display_df = display_df[['Rank', 'title', 'word_count', 'unique_word_count',
                                         'lexical_diversity', 'annotation_count', 'complexity_score']]
                display_df.columns = ['Rank', 'Song', 'Word Count', 'Unique Words',
                                      'Lexical Diversity', 'Annotations', 'Complexity Score']

                # Display the table
                st.dataframe(display_df, use_container_width=True)

                # Add an explanation of the complexity score
                with st.expander("How is the Complexity Score calculated?"):
                    st.markdown(f"""
                    The complexity score is a weighted combination of:
                    - **Lexical Diversity** (weight: {WEIGHTS['lexical_diversity']:.1f}): The ratio of unique words to total words
                    - **Annotation Density** (weight: {WEIGHTS['annotation_density']:.1f}): The number of annotations relative to song length

                    The score is normalized so that the highest possible value is 1.0.
                    """)
            else:
                st.info("No song rankings available. This may be because only one song was analyzed.")

        # Visualizations tab
        with results_tabs[2]:
            st.header("Visualizations")

            # Check if we have ranked songs
            if ranked_songs is not None and not ranked_songs.empty and len(ranked_songs) > 1:
                # Create a visualization
                temp_viz_path = f"{artist_name.replace(' ', '_')}_complexity_analysis.png"

                # Check if output_files has the visualization
                if 'output_files' in results and 'visualization_file' in results['output_files']:
                    viz_path = results['output_files']['visualization_file']
                    if os.path.exists(viz_path):
                        # Display the existing visualization
                        st.image(viz_path, use_column_width=True)

                        # Add download button
                        with open(viz_path, "rb") as file:
                            st.download_button(
                                label="Download Visualization",
                                data=file,
                                file_name=os.path.basename(viz_path),
                                mime="image/png"
                            )
                    else:
                        st.info("Visualization file not found.")
                else:
                    # We need to create a new visualization
                    # First, initialize the analyzer if it's not defined
                    if 'analyzer' not in locals() and 'analyzer' not in globals():
                        try:
                            analyzer = GeniusLyricsAnalyzer(token)
                            # Now create the visualization
                            viz_created = analyzer.visualize_song_complexity(ranked_songs, save_path=temp_viz_path,
                                                                             status_callback=None)

                            if viz_created and os.path.exists(temp_viz_path):
                                # Display the visualization
                                st.image(temp_viz_path, use_column_width=True)

                                # Add download button for the visualization
                                with open(temp_viz_path, "rb") as file:
                                    st.download_button(
                                        label="Download Visualization",
                                        data=file,
                                        file_name=os.path.basename(temp_viz_path),
                                        mime="image/png"
                                    )

                                # If save_files is False, remove the file after displaying
                                if not save_files:
                                    try:
                                        os.remove(temp_viz_path)
                                    except:
                                        pass  # Ignore if file can't be removed
                            else:
                                st.info("Visualization could not be created.")
                        except:
                            st.error("Could not create visualization. Try running the analysis again.")
                    else:
                        # Use the existing analyzer
                        try:
                            viz_created = analyzer.visualize_song_complexity(ranked_songs, save_path=temp_viz_path,
                                                                             status_callback=None)

                            if viz_created and os.path.exists(temp_viz_path):
                                # Display the visualization
                                st.image(temp_viz_path, use_column_width=True)

                                # Add download button for the visualization
                                with open(temp_viz_path, "rb") as file:
                                    st.download_button(
                                        label="Download Visualization",
                                        data=file,
                                        file_name=os.path.basename(temp_viz_path),
                                        mime="image/png"
                                    )

                                # If save_files is False, remove the file after displaying
                                if not save_files:
                                    try:
                                        os.remove(temp_viz_path)
                                    except:
                                        pass  # Ignore if file can't be removed
                            else:
                                st.info("Visualization could not be created.")
                        except:
                            st.error("Could not create visualization. Try running the analysis again.")

                # Explanation
                st.markdown("""
                **Top Chart**: Songs ranked by their overall complexity score.

                **Bottom Chart**: Scatter plot showing the relationship between lexical diversity (vocabulary richness) 
                and annotation density (how much of the song has annotations on Genius).
                """)
            elif len(songs_df) <= 1:
                st.info("Visualizations require at least 2 songs to compare. Try analyzing more songs.")
            else:
                st.info("No visualization available.")

            # Add download buttons for CSV files
            if not songs_df.empty:
                st.subheader("Data Downloads")

                col1, col2 = st.columns(2)

                with col1:
                    # Download button for songs analysis
                    csv_songs = songs_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Songs Analysis CSV",
                        data=csv_songs,
                        file_name=f"{artist_name.replace(' ', '_')}_songs_analysis.csv",
                        mime="text/csv"
                    )

                with col2:
                    if not annotations_df.empty:
                        # Download button for annotations
                        csv_annotations = annotations_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Annotations CSV",
                            data=csv_annotations,
                            file_name=f"{artist_name.replace(' ', '_')}_annotations.csv",
                            mime="text/csv"
                        )

        # Annotations tab
        with results_tabs[3]:
            st.header("Lyrics and Annotations")

            if annotations_df is not None and not annotations_df.empty:
                # Group by song
                song_titles = annotations_df['title'].unique()

                # Song selector
                selected_song = st.selectbox("Select a song", song_titles)

                # Get annotations for selected song
                song_annotations = annotations_df[annotations_df['title'] == selected_song]

                if not song_annotations.empty:
                    st.subheader(f"Annotations for '{selected_song}'")

                    # Display annotations
                    for i, row in song_annotations.iterrows():
                        with st.expander(f"Lyric: \"{row['lyric_fragment'][:50]}...\""):
                            st.markdown(f"""
                            <div class="annotation-box">
                                <div class="lyric-fragment">"{row['lyric_fragment']}"</div>
                                <p>{row['annotation']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No annotations found for this song.")
            else:
                st.info("No annotations available.")

        with results_tabs[4]:
            st.header("Songwriter's Workshop")
            st.markdown("Use insights from your analysis to inspire your own songwriting")

            # If no analysis has been run yet, show a message
            if not st.session_state.results:
                st.info("Run an analysis first to get inspiration for your songwriting!")
                st.markdown("""
                **Tip**: Try analyzing songs by artists you admire or in the style you want to write.
                The workshop tools will help you apply those insights to your own lyrics.
                """)
            else:
                # Get data from the analysis
                results = st.session_state.results
                songs_df = results.get('songs_df')
                ranked_songs = results.get('ranked_songs')
                annotations_df = results.get('annotations_df')

                # Create columns for different tools
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Lyrical Complexity Target")

                    if ranked_songs is not None and not ranked_songs.empty:
                        # Get the average complexity scores
                        avg_lexical_diversity = songs_df['lexical_diversity'].mean()

                        # Calculate average annotation density safely
                        if 'annotation_count' in songs_df.columns and 'word_count' in songs_df.columns:
                            # Replace zeros with ones to avoid division by zero
                            word_counts = songs_df['word_count'].replace(0, 1)
                            avg_annotation_density = (songs_df['annotation_count'] / word_counts).mean()
                        else:
                            avg_annotation_density = 0.0

                        st.markdown(f"""
                        Based on your analysis, these songs have:
                        - Average vocabulary richness: {avg_lexical_diversity:.4f}
                        - Average annotation density: {avg_annotation_density:.4f}

                        These can be your targets for lyrical complexity.
                        """)

                        # Add slider to set target complexity
                        st.markdown("#### Set your target complexity")
                        target_complexity = st.slider(
                            "Vocabulary richness target",
                            min_value=0.0,
                            max_value=1.0,
                            value=float(avg_lexical_diversity),
                            step=0.01
                        )

                        if target_complexity < 0.3:
                            st.markdown("💡 **Low complexity**: Simple, accessible lyrics with repeated phrases")
                        elif target_complexity < 0.5:
                            st.markdown("💡 **Medium complexity**: Balanced vocabulary with some unique phrases")
                        else:
                            st.markdown("💡 **High complexity**: Rich, diverse vocabulary with many unique words")
                    else:
                        st.info("Analyze multiple songs to get complexity targets")

                with col2:
                    st.subheader("Theme Inspiration")

                    if annotations_df is not None and not annotations_df.empty:
                        # Extract themes from annotations
                        all_annotations = " ".join(annotations_df['annotation'].tolist())

                        # List of common theme words to look for
                        theme_words = [
                            "love", "heartbreak", "struggle", "hope", "freedom",
                            "identity", "change", "time", "memory", "loss",
                            "power", "conflict", "journey", "transformation", "nature",
                            "society", "politics", "religion", "faith", "doubt",
                            "joy", "pain", "longing", "desire", "fear"
                        ]

                        # Count occurrences of theme words
                        theme_counts = {}
                        for theme in theme_words:
                            count = all_annotations.lower().count(theme)
                            if count > 0:
                                theme_counts[theme] = count

                        # Sort by count
                        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)

                        # Display top themes
                        st.markdown("Common themes in these songs:")

                        if sorted_themes:
                            for theme, count in sorted_themes[:5]:
                                st.markdown(f"- **{theme.title()}** ({count} mentions)")

                            # Suggest combining themes
                            if len(sorted_themes) >= 2:
                                import random

                                theme1, theme2 = random.sample([t[0] for t in sorted_themes[:5]], 2)
                                st.markdown(f"""
                                💡 **Theme idea**: Try combining **{theme1}** and **{theme2}** 
                                in an unexpected way
                                """)
                        else:
                            st.markdown("No common themes found. Try analyzing more songs.")
                    else:
                        st.info("Analyze songs with annotations to get theme inspiration")

                # Lyric drafting area
                st.subheader("Lyric Drafting Area")

                # Initialize session state for lyrics if it doesn't exist
                if 'lyrics_draft' not in st.session_state:
                    st.session_state.lyrics_draft = ""

                # Create a text area for lyrics drafting
                lyrics_text = st.text_area(
                    "Write your lyrics here",
                    value=st.session_state.lyrics_draft,
                    height=300,
                    key="lyrics_drafting"
                )

                # Update session state when text changes
                st.session_state.lyrics_draft = lyrics_text

                # Add analysis button
                if st.button("Analyze My Lyrics"):
                    if not lyrics_text.strip():
                        st.warning("Please write some lyrics first!")
                    else:
                        # Perform basic analysis on the draft lyrics
                        words = lyrics_text.split()
                        word_count = len(words)
                        unique_words = len(set(word.lower() for word in words))

                        if word_count > 0:
                            lexical_diversity = unique_words / word_count

                            # Compare to target if set
                            if 'target_complexity' in locals():
                                if lexical_diversity < target_complexity * 0.8:
                                    suggestion = "Try adding more unique words to increase complexity"
                                elif lexical_diversity > target_complexity * 1.2:
                                    suggestion = "Consider using more repetition to decrease complexity"
                                else:
                                    suggestion = "Your vocabulary richness is on target!"
                            else:
                                suggestion = ""

                            # Display analysis
                            st.markdown(f"""
                            #### Lyrics Analysis
                            - Word count: {word_count}
                            - Unique words: {unique_words}
                            - Vocabulary richness: {lexical_diversity:.4f}

                            {suggestion}
                            """)

                            # Find potential rhymes
                            st.markdown("#### Rhyme Analysis")

                            # Get last words of each line
                            lines = [line.strip() for line in lyrics_text.split('\n') if line.strip()]
                            if lines:
                                last_words = [line.split()[-1].lower().strip('.,!?;:"\'') for line in lines if
                                              line.split()]

                                # Find rhyming patterns
                                rhyme_pattern = []
                                rhyme_groups = {}
                                current_letter = 'A'

                                for word in last_words:
                                    # Very simple rhyme detection based on last 2 characters
                                    # A more sophisticated system would use phonetics
                                    ending = word[-2:] if len(word) >= 2 else word

                                    if ending in rhyme_groups:
                                        rhyme_pattern.append(rhyme_groups[ending])
                                    else:
                                        rhyme_groups[ending] = current_letter
                                        rhyme_pattern.append(current_letter)
                                        current_letter = chr(ord(current_letter) + 1)

                                # Display rhyme pattern
                                st.markdown(f"Detected rhyme pattern: **{''.join(rhyme_pattern)}**")

                        # Simple word frequency analysis
                        if word_count > 10:
                            # Clean words
                            import re
                            import string

                            clean_words = [re.sub(f'[{string.punctuation}]', '', word.lower()) for word in words]
                            clean_words = [word for word in clean_words if word and len(word) > 2]

                            # Count frequencies
                            from collections import Counter

                            word_counts = Counter(clean_words)

                            # Show most frequent words
                            st.markdown("#### Most used words:")
                            most_common = word_counts.most_common(5)
                            for word, count in most_common:
                                st.markdown(f"- **{word}**: {count} times")

                            # Check for overused words
                            if most_common and most_common[0][1] > word_count * 0.1:
                                st.markdown(f"""
                                💡 **Tip**: The word "**{most_common[0][0]}**" appears frequently. 
                                Consider using synonyms or different phrasing if it feels repetitive.
                                """)

                # Add a rhyme suggestion tool
                st.subheader("Rhyme Suggester")
                rhyme_word = st.text_input("Enter a word to find rhymes for:")

                if rhyme_word:
                    # Simple rhyme suggestion based on word endings
                    # In a full implementation, you'd use a phonetic rhyming dictionary
                    st.markdown("#### Words that might rhyme:")

                    # Get all unique words from the analyzed songs
                    all_words = set()
                    if songs_df is not None and not songs_df.empty:
                        for song_data in results.get('processed_songs', []):
                            if song_data and 'lyrics' in song_data:
                                lyrics = song_data['lyrics']
                                # Clean and extract words
                                import re

                                words_in_lyrics = re.findall(r'\b\w+\b', lyrics.lower())
                                all_words.update(words_in_lyrics)

                    # Find potential rhymes based on endings
                    ending = rhyme_word[-2:] if len(rhyme_word) >= 2 else rhyme_word
                    potential_rhymes = [word for word in all_words if
                                        word.endswith(ending) and word != rhyme_word.lower()]

                    # Display suggestions
                    if potential_rhymes:
                        import random

                        suggestions = random.sample(potential_rhymes, min(5, len(potential_rhymes)))
                        for word in suggestions:
                            st.markdown(f"- {word}")
                    else:
                        st.markdown("No rhyme suggestions found in the analyzed songs.")

                        # Provide some common rhyming words
                        common_endings = {
                            'ay': ['day', 'way', 'say', 'play', 'stay'],
                            'ight': ['night', 'light', 'fight', 'right', 'sight'],
                            'ove': ['love', 'above', 'dove', 'shove', 'glove'],
                            'own': ['down', 'town', 'crown', 'frown', 'gown'],
                            'ame': ['fame', 'game', 'name', 'same', 'flame']
                        }

                        for end, words in common_endings.items():
                            if rhyme_word.endswith(end):
                                st.markdown("Common rhymes:")
                                for word in words:
                                    if word != rhyme_word.lower():
                                        st.markdown(f"- {word}")
                                break
    else:
        # No results yet or empty results
        for tab in results_tabs:
            with tab:
                st.info("Run an analysis to see results here.")
else:
    # No results yet
    for tab in results_tabs:
        with tab:
            st.info("Run an analysis to see results here.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and the Genius API")